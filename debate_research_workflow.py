import os
from dotenv import load_dotenv
from tavily import TavilyClient
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage
from pydantic import BaseModel
import json
import asyncio
from typing import List, Dict
from podcast_script_generator import generate_podcast_script

load_dotenv()

# Set up Azure OpenAI environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
os.environ["OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION")

class StancePackage(Event):
    stance: str
    stance_type: str  # "for" or "against"

class StanceSourceMaterialPackage(Event):
    stance_source_materials: str
    urls: List[str]
    stance_type: str

class SourceMaterialPackage(Event):
    source_materials_for: str
    source_materials_against: str
    urls_for: List[str]
    urls_against: List[str]

class StanceEssayPackage(Event):
    essay: str
    stance_type: str
    reference_urls: List[str]

class EssayTask(Event):
    source_materials: str
    urls: List[str]
    stance_type: str
    topic: str

class Stances(BaseModel):
    """Stance for and against the topic"""
    stance_for: str
    stance_against: str

class DebateResearchWorkflow(Workflow):
    @step
    async def identify_stances(self, ctx: Context, ev: StartEvent) -> StancePackage:
        topic = ev.query
        print(f'topic: {topic}')
        await ctx.set('topic', topic)

        # Initial research to understand the topic
        tavily_client = TavilyClient()
        sanitized_query = sanitize_search_query(topic)
        print(f'Sanitized search query: "{sanitized_query}"')  # Debug logging
        response = tavily_client.search(sanitized_query)
        source_materials = '\n'.join(result['content'] for result in response['results'])
        initial_urls = [result['url'] for result in response['results']]
        await ctx.set('initial_urls', initial_urls)

        # Use LLM to identify the stances
        llm = AzureOpenAI(
            engine="o3-mini",
            model="o3-mini",
            temperature=0.3
        )
        sllm = llm.as_structured_llm(output_cls=Stances)
        input_msg = ChatMessage.from_str(f'''Given this debate topic '{topic}' and these initial materials: {source_materials}
                                        Generate two clear opposing stances - one for and one against the topic.
                                        Each stance should be a clear position statement, not longer than 15 words.''')
        response = sllm.chat([input_msg])
        stances = json.loads(response.message.content)
        
        # Send events for both stances
        ctx.send_event(StancePackage(stance=stances["stance_for"], stance_type="for"))
        ctx.send_event(StancePackage(stance=stances["stance_against"], stance_type="against"))

    @step(num_workers=2)
    async def research_stance(self, ctx: Context, ev: StancePackage) -> StanceSourceMaterialPackage:
        stance = ev.stance
        stance_type = ev.stance_type
        
        tavily_client = TavilyClient()
        response = tavily_client.search(sanitize_search_query(stance))
        stance_materials = '\n'.join(result['content'] for result in response['results'])
        stance_urls = [result['url'] for result in response['results']]
        
        return StanceSourceMaterialPackage(
            stance_source_materials=stance_materials,
            urls=stance_urls,
            stance_type=stance_type
        )

    @step
    async def combine_stance_research(self, ctx: Context, ev: StanceSourceMaterialPackage) -> EssayTask:
        source_materials = ctx.collect_events(ev, [StanceSourceMaterialPackage] * 2)
        if source_materials is None:
            return None

        # Get topic
        topic = await ctx.get('topic')

        # Send essay tasks for both stances
        for material in source_materials:
            ctx.send_event(EssayTask(
                source_materials=material.stance_source_materials,
                urls=material.urls,
                stance_type=material.stance_type,
                topic=topic
            ))

    @step(num_workers=2)
    async def write_stance_essay(self, ctx: Context, ev: EssayTask) -> StanceEssayPackage:
        llm = AzureOpenAI(
            engine="gpt-4o-mini",
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=10000
        )
        
        prompt = f'''You are writing a persuasive essay {ev.stance_type} this topic: {ev.topic}
                    Use these source materials to support your argument: {ev.source_materials}
                    
                    First, identify your three main arguments. Each should be summarized in 3-5 words.
                    Then, write the essay using these EXACT section headers and structure:

                    # Introduction
                    [First paragraph: Present the topic and its significance]
                    
                    [Second paragraph: Clearly state your position ({ev.stance_type} the topic)]

                    # Main Arguments

                    ## Key Point 1: [Your first main argument in 3-5 words]
                    [Topic sentence followed by supporting evidence and examples]
                    [End with a concluding sentence]

                    ## Key Point 2: [Your second main argument in 3-5 words]
                    [Topic sentence followed by supporting evidence and examples]
                    [End with a concluding sentence]

                    ## Key Point 3: [Your third main argument in 3-5 words]
                    [Topic sentence followed by supporting evidence and examples]
                    [End with a concluding sentence]

                    # Addressing Counter-Arguments
                    [Present and address opposing viewpoints]
                    [Explain why your position is more compelling]

                    # Conclusion
                    [First paragraph: Summarize main arguments]
                    
                    [Second paragraph: Reinforce position and implications]

                    Format Requirements:
                    1. Use the EXACT section headers shown above with # and ##
                    2. Replace [Your first/second/third main argument] with actual 3-5 word argument summaries
                    3. Double line break between sections and paragraphs
                    4. Each paragraph should be 4-6 sentences
                    5. Use transition words between sections
                    6. Maintain formal academic tone
                    7. Cite sources when presenting evidence using (Source: URL)
                    
                    Write the essay now, following this structure and formatting exactly.'''
                    
        response = await llm.acomplete(prompt)
        
        return StanceEssayPackage(
            essay=str(response),
            stance_type=ev.stance_type,
            reference_urls=ev.urls
        )

    @step
    async def finalize_essays(self, ctx: Context, ev: StanceEssayPackage) -> StopEvent:
        essays = ctx.collect_events(ev, [StanceEssayPackage] * 2)
        if essays is None:
            return None
            
        # Combine essays into final result
        essay_for = next(e for e in essays if e.stance_type == "for")
        essay_against = next(e for e in essays if e.stance_type == "against")
        
        return StopEvent(result={
            "for": {
                "essay": essay_for.essay,
                "references": essay_for.reference_urls
            },
            "against": {
                "essay": essay_against.essay,
                "references": essay_against.reference_urls
            }
        })

def sanitize_search_query(query: str) -> str:
    """Clean the search query by removing non-printable characters and excess whitespace."""
    if not query:
        return ""
    
    # Convert to string if not already
    query = str(query)
    
    # Replace newlines, tabs, and other common whitespace characters
    query = query.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    # Remove any other non-printable characters
    query = ''.join(char for char in query if char.isprintable())
    
    # Normalize whitespace and strip
    query = ' '.join(query.split()).strip()
    
    # Ensure the query is not empty after cleaning
    if not query:
        raise ValueError("Search query is empty after sanitization")
        
    return query

async def research_debate_topic(topic: str) -> Dict:
    """
    Research a debate topic and generate essays for both stances.
    Returns a dictionary containing both essays and their references.
    """
    os.makedirs('output', exist_ok=True)
    
    w = DebateResearchWorkflow(timeout=10000, verbose=False)
    result = await w.run(query=topic)
    
    # Save essays to markdown files
    for stance in ["for", "against"]:
        essay = result[stance]["essay"]
        references = result[stance]["references"]
        
        markdown_content = f"# {topic.title()} - {stance.title()} Stance\n\n"
        markdown_content += f"{essay}\n\n## References\n"
        for i, url in enumerate(references, 1):
            markdown_content += f"{i}. {url}\n"
            
        filename = f"output/{topic.replace(' ', '_').lower()}_{stance}_stance.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    return result 