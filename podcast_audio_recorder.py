import os
import json
import asyncio
from azure.cognitiveservices.speech import (
    SpeechConfig, 
    SpeechSynthesizer, 
    AudioConfig,
    ResultReason
)
from dotenv import load_dotenv
from typing import Dict, List
import wave
import io
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import random

# Load environment variables
load_dotenv()

class PodcastAudioRecorder:
    def __init__(self):
        """Initialize the audio recorder with Azure Speech configuration."""
        self.speech_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
        self.service_region = os.getenv("AZURE_SERVICE_REGION")
        
        if not self.speech_key or not self.service_region:
            raise ValueError("Azure Speech credentials not found in environment variables")
            
        self.speech_config = SpeechConfig(
            subscription=self.speech_key,
            region=self.service_region
        )
        
        # Rate limiting settings - increase delay and add jitter
        self.request_delay = 1.0  # Base delay of 1 second
        self.jitter = 0.5  # Add random jitter of up to 0.5 seconds
        self.last_request_time = 0
        self.consecutive_429s = 0  # Track consecutive 429 errors
        self.max_429_backoff = 30  # Maximum backoff in seconds

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits by adding delay between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Calculate delay with jitter and potential backoff
        base_delay = self.request_delay
        if self.consecutive_429s > 0:
            # Exponential backoff when hitting rate limits
            backoff = min(2 ** self.consecutive_429s, self.max_429_backoff)
            base_delay += backoff
        
        # Add random jitter
        delay = base_delay + random.uniform(0, self.jitter)
        
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(5),  # Increase retry attempts
        wait=wait_exponential(multiplier=2, min=4, max=30),  # Increase wait times
        reraise=True
    )
    async def generate_audio_segment(self, text: str, voice_name: str, output_path: str) -> bool:
        """Generate audio for a single line of dialogue with retry logic."""
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Configure speech synthesis for this segment
        self.speech_config.speech_synthesis_voice_name = voice_name
        
        # Create audio configuration for file output
        audio_config = AudioConfig(filename=output_path)
        
        # Create speech synthesizer
        synthesizer = SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        try:
            # Generate speech and wait for completion
            result = synthesizer.speak_text_async(text).get()
            success = result.reason == ResultReason.SynthesizingAudioCompleted
            
            if not success:
                print(f"Error synthesizing audio: {result.reason}")
                if result.cancellation_details:
                    error_details = result.cancellation_details
                    print(f"Error details: {error_details.reason}")
                    print(f"Error code: {error_details.error_code}")
                    print(f"Error message: {error_details.error_details}")
                    
                    # If we hit rate limit, update counter and raise for retry
                    if "429" in str(error_details.error_code):
                        self.consecutive_429s += 1
                        raise Exception("Rate limit exceeded")
                    
            if success:
                self.consecutive_429s = 0  # Reset counter on success
                # Add a small delay after successful generation
                await asyncio.sleep(0.5)  # 0.5 second delay after each successful generation
            return success
            
        except Exception as e:
            print(f"Exception during audio generation: {str(e)}")
            raise

    def combine_audio_files(self, input_files: List[str], output_file: str):
        """Combine multiple WAV files into a single file."""
        # Read the first file to get audio parameters
        with wave.open(input_files[0], 'rb') as first_wav:
            params = first_wav.getparams()
        
        # Create output WAV file
        with wave.open(output_file, 'wb') as output_wav:
            output_wav.setparams(params)
            
            # Write all files
            for input_file in input_files:
                with wave.open(input_file, 'rb') as wav:
                    output_wav.writeframes(wav.readframes(wav.getnframes()))

    async def generate_podcast_audio(self, script_data: Dict) -> str:
        """
        Generate audio for the entire podcast script.
        
        Args:
            script_data: Dictionary containing the podcast script
            
        Returns:
            Path to the generated audio file
        """
        topic = script_data["topic"]
        dialogue = script_data["dialogue"]
        voices = script_data["voices"]
        
        print(f"Generating audio for podcast: {topic}")
        print(f"Number of dialogue lines: {len(dialogue)}")
        
        # Create temporary directory for segments
        os.makedirs('temp_audio', exist_ok=True)
        segment_files = []
        failed_segments = []
        
        # Generate audio for each line
        for i, line in enumerate(dialogue, 1):
            role = line["role"]
            text = line["text"]
            voice = voices[role]
            
            print(f"Processing line {i}/{len(dialogue)} - {role}")
            segment_path = f"temp_audio/segment_{i}.wav"
            
            try:
                # Wait for the previous segment to complete and add delay
                await asyncio.sleep(1)  # 1 second base delay between segments
                
                success = await self.generate_audio_segment(text, voice, segment_path)
                if success:
                    segment_files.append(segment_path)
                else:
                    failed_segments.append(i)
                    print(f"Failed to generate audio for line {i}")
            except Exception as e:
                failed_segments.append(i)
                print(f"Exception processing line {i}: {str(e)}")
            
            # Add a longer pause every 5 lines to avoid rate limiting
            if i % 5 == 0:
                print(f"Pausing for 5 seconds after line {i}...")
                await asyncio.sleep(5)
        
        if not segment_files:
            raise Exception("No audio segments were generated successfully")
        
        if failed_segments:
            print(f"Warning: Failed to generate audio for {len(failed_segments)} lines: {failed_segments}")
        
        # Create output directory and final path
        os.makedirs('output', exist_ok=True)
        output_path = f"output/{topic.replace(' ', '_').lower()}_podcast.wav"
        
        # Combine all segments
        print("Combining audio segments...")
        self.combine_audio_files(segment_files, output_path)
        
        # Clean up temporary files
        for file in segment_files:
            try:
                os.remove(file)
            except:
                pass
        try:
            os.rmdir('temp_audio')
        except:
            pass
            
        print(f"Audio saved to: {output_path}")
        return output_path

async def main():
    # Test script
    test_script = {
        "topic": "Test Podcast",
        "dialogue": [
            {"role": "MODERATOR", "text": "Welcome to our test podcast! Today we're discussing an important topic."},
            {"role": "FOR DEBATOR", "text": "I'm excited to be here and share my perspective."},
            {"role": "AGAINST DEBATOR", "text": "Thank you for having us. Looking forward to a great discussion."},
            {"role": "MODERATOR", "text": "Let's begin with our first point of discussion..."}
        ],
        "voices": {
            "MODERATOR": "en-US-GuyNeural",
            "FOR DEBATOR": "en-US-TonyNeural",
            "AGAINST DEBATOR": "en-US-JennyNeural"
        }
    }
    
    try:
        recorder = PodcastAudioRecorder()
        audio_path = await recorder.generate_podcast_audio(test_script)
        print(f"Success! Audio generated at: {audio_path}")
    except Exception as e:
        print(f"Error generating audio: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 