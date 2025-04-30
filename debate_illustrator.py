import os
from llama_index.llms.azure_openai import AzureOpenAI 
from openai import OpenAI as oai
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Set up Azure OpenAI environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION")

def download_image(url: str, save_path: str) -> bool:
    """Download an image from a URL and save it to disk"""
    response = requests.get(url)
    if response.status_code == 200:
        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print('Debate illustration successfully downloaded and saved')
        return True
    else:
        print('Failed to download debate illustration')
        return False

async def generate_debate_illustration(topic: str, for_stance: str, against_stance: str) -> str:
    """Generate an illustration for a debate scene with specific characters"""
    # First, generate the prompt using GPT-4
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    prompt_text = f'''You are a veteran illustration artist specializing in debate and discussion scenes.

Create a DALL-E prompt for an illustration of a professional debate scene with these specific requirements:

Topic being debated: {topic}

Required elements:
1. A professional male moderator in the center
2. A male debater named MR. YES on one side (for stance)
3. A female debater named MS. NO on the other side (against stance)
4. Modern debate stage or studio setting
5. Visual elements that represent the debate topic

Style requirements:
- Watercolor cartoon anime art style
- High detail on facial expressions showing engagement

Write only the DALL-E prompt, no other text.'''
    
    prompt_response = llm.complete(prompt_text)
    draw_prompt = str(prompt_response)
    print(f"Generated prompt: {draw_prompt}")
    
    # Generate the image using DALL-E
    client = oai(api_key=os.getenv("OPENAI_API_KEY_REGULAR"))
    response = client.images.generate(
        model="dall-e-3",
        prompt=draw_prompt,
        size="1024x1024",
        quality="hd",
        n=1
    )

    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")
    
    # Create output directory and path
    output_path = f"output/debate_illustration_{topic.replace(' ', '_').lower()}.png"
    
    # Download and save the image
    if download_image(image_url, output_path):
        return output_path
    return None

async def main():
    # Test the illustration generation
    topic = "Should AI be regulated?"
    for_stance = "AI regulation is necessary for safety and ethical development"
    against_stance = "Excessive regulation could stifle innovation and progress"
    
    illustration_path = await generate_debate_illustration(topic, for_stance, against_stance)
    
    if illustration_path:
        print(f"Illustration has been generated and saved to {illustration_path}")
    else:
        print("Failed to generate illustration")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 