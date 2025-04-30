import json
import os
from typing import Dict, List
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Azure OpenAI environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION")

class PodcastScriptGenerator:
    def __init__(self):
        self.llm = AzureOpenAI(
            engine="gpt-4o-mini",
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=10000
        )

    async def generate_script(self, topic: str, for_essay: str, against_essay: str) -> Dict:
        """Generate a podcast script from the debate essays."""
        
        prompt = f'''Create an engaging podcast debate script about "{topic}" using these essays.
                    For stance essay: {for_essay}
                    Against stance essay: {against_essay}

                    Create a natural dialogue between three roles:
                    [MODERATOR]: Guides discussion, asks questions, maintains balance
                    [MR. YES]: Presents arguments for the topic with confidence and enthusiasm
                    [MS. NO]: Presents arguments against the topic with skepticism and wit

                    The script should follow this structure:

                    1. Introduction
                    - [MODERATOR] welcomes audience, introduces topic
                    - [MODERATOR] introduces debators and format
                    - Each debator gives 30-second opening statement

                    2. Main Discussion (3 rounds)
                    For each key point:
                    - [MODERATOR] introduces the subtopic
                    - [MR. YES] presents argument with conviction and passion
                    - [MS. NO] responds with skepticism and clever counterpoints
                    - Allow brief back-and-forth with some friendly banter
                    - [MODERATOR] summarizes and transitions

                    3. Counter-Arguments Section
                    - [MODERATOR] asks each side to address opposing views
                    - Each debator responds to main counter-arguments
                    - Brief discussion of points of agreement/disagreement

                    4. Closing Statements
                    - Each debator gives 45-second closing statement
                    - [MODERATOR] summarizes key points and concludes

                    IMPORTANT: Format your response EXACTLY like this example:
                    [MODERATOR]: Welcome to today's debate on...
                    [MR. YES]: Thank you. I believe that...
                    [MS. NO]: I appreciate the opportunity to...
                    
                    Keep each line under 50 words for better TTS processing.
                    Use natural, conversational language while maintaining professionalism.
                    Add some attitude and spiciness to MR. YES and MS. NO's dialogue - they should have distinct personalities:
                    - MR. YES should be enthusiastic, optimistic, and sometimes a bit over-the-top in his support
                    - MS. NO should be skeptical, witty, and occasionally sarcastic in her opposition
                    Make sure to include all sections of the debate structure.'''

        response = await self.llm.acomplete(prompt)
        
        # Parse the response into dialogue entries
        lines = str(response).strip().split('\n')
        script = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for role markers
            if '[MODERATOR]:' in line:
                role = 'MODERATOR'
                text = line.split('[MODERATOR]:')[1].strip()
            elif '[MR. YES]:' in line:
                role = 'MR. YES'
                text = line.split('[MR. YES]:')[1].strip()
            elif '[MS. NO]:' in line:
                role = 'MS. NO'
                text = line.split('[MS. NO]:')[1].strip()
            else:
                continue
                
            if text:  # Only add if we have actual text content
                script.append({"role": role, "text": text})

        # Verify we have content
        if not script:
            print("Warning: No dialogue was generated. Raw response:")
            print(str(response))
            script = [{"role": "MODERATOR", "text": "Error: Failed to generate proper dialogue."}]

        # Save the script to a JSON file
        os.makedirs('output', exist_ok=True)
        filename = f"output/{topic.replace(' ', '_').lower()}_podcast_script.json"
        
        script_data = {
            "topic": topic,
            "dialogue": script,
            "voices": {
                "MODERATOR": "en-US-GuyNeural",
                "MR. YES": "en-US-TonyNeural",
                "MS. NO": "en-US-JennyNeural"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
            
        return script_data

async def generate_podcast_script(topic: str, for_essay: str, against_essay: str) -> Dict:
    """
    Generate a podcast script from debate essays.
    Returns a dictionary containing the script and voice assignments.
    """
    generator = PodcastScriptGenerator()
    return await generator.generate_script(topic, for_essay, against_essay)

# Test code
async def test_script_generation():
    # Example topic and essays
    topic = "Should AI be regulated?"
    
    # Example for stance essay (shortened for testing)
    for_essay = """
    # Introduction
    Artificial Intelligence regulation is a critical issue in today's rapidly evolving technological landscape. The potential impact of AI on society, economy, and human rights demands careful oversight.

    # Main Arguments

    ## Key Point 1: Public Safety Protection
    AI systems can pose significant risks without proper safeguards. We need comprehensive regulations to ensure AI systems are safe and reliable.

    ## Key Point 2: Ethical Development Framework
    Regulation provides clear guidelines for ethical AI development, preventing misuse and ensuring responsible innovation.

    ## Key Point 3: Global Standards Necessity
    International cooperation through regulation is essential to prevent a race to the bottom in AI safety standards.

    # Conclusion
    Regulation is essential for ensuring AI benefits society while minimizing risks.
    """
    
    # Example against stance essay
    against_essay = """
    # Introduction
    While AI safety is important, heavy-handed regulation could stifle innovation and technological progress. A more flexible approach is needed.

    # Main Arguments

    ## Key Point 1: Innovation Hindrance
    Strict regulations could slow down AI development and put us at a competitive disadvantage.

    ## Key Point 2: Self-Regulation Effectiveness
    The tech industry has shown capability in self-regulation through voluntary guidelines and standards.

    ## Key Point 3: Market-Driven Solutions
    Market forces naturally incentivize companies to develop safe and ethical AI systems.

    # Conclusion
    Industry self-regulation and market forces are more effective than government intervention.
    """
    
    # Generate script
    script_data = await generate_podcast_script(topic, for_essay, against_essay)
    
    # Print the generated script in a readable format
    print(f"\nGenerated Podcast Script for topic: {topic}\n")
    print("=" * 80 + "\n")
    
    for entry in script_data["dialogue"]:
        role = entry["role"]
        text = entry["text"]
        print(f"[{role}]: {text}\n")

if __name__ == "__main__":
    asyncio.run(test_script_generation()) 