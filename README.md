# For My Wife 👩💚

🔗 **Try it out**: [https://formywife.streamlit.app/](https://formywife.streamlit.app/)

### There are also a sample debate podcast file inside the 'samples' folder

![App Screenshot](app_screenshot.png)

## Overview

My wife takes a long time before making any life decisions, whether it is to try on new diet or to get a new pair of shoes. Thorough research is a must and hasty impulsive purchases are not tolerated. I know she is not alone.

**For My Wife** is a multi-agentic research system designed to help ANYONE gain multifaceted insights and make informed decisions on ANY TOPICS, be it personal matters like e-commerce spending or lifestyle choices, to professional ones like marketing strategies for a new customer segment. The app uses AI to generate COMPREHENSIVE DEBATES between AI researchers, providing balanced perspectives on any subject matter. This debate format is intended to deliver the researched insights in an engaging and memorable manner to people who enjoy watching dramas like my wife.

This project was created to save time on research when making decisions, offering a comprehensive understanding of topics through deep research, structured debates, visual illustrations, and audio presentations.

## Features

- **Comprehensive Research**: Analyzes topics and identifies diverse, opposing perspectives for deep research
- **Visual Debates**: Generates custom illustrations
- **Structured Essays**: Creates well-researched essays supporting each position
- **Interactive Podcasts**: Produces debate scripts with a moderator and two debaters.
- **Audio Generation**: Converts scripts to audio using different voices for each speaker
- **Downloadable Content**: Save illustrations, scripts, and audio recordings

## System Architecture

![System Architecture Diagram](for_my_wife_diagram.png)

The application follows a multi-agent architecture where different AI agents collaborate to create a comprehensive research and debate experience:

1. **Research Flow**:
   - The process begins with a debate topic input
   - A top research agent performs high-level web research to gather general materials
   - The materials are then distributed to two specialized research agents:
     - FOR stance research agent with its own detailed web research
     - AGAINST stance research agent with its own detailed web research
   - Both agents write research essays for their argument for display and contribute to creating the debate content

2. **Content Generation Flow**:
   - The debate content feeds into the audio generation process:
       - A writer agent creates structured debate scripts with MODERATOR, MR. YES, and MS. NO.
       - Voice agents convert the scripts into audio using different voices for each role

3. **Illustration Flow**: 
   - An illustrator agent is given the topic of the debate and creates a custom illustration for the debate in parallel with the research and content generation flow.

This architecture ensures that each aspect of the debate (research, visuals, and audio) is handled by specialized agents, resulting in high-quality, well-researched, and engaging content.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/for_my_wife.git
   cd for_my_wife
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Enter any topic you need to research for decision-making

4. Click "Fight!!!" to generate comprehensive research and debates

5. Explore the research in the three tabs:
   - **For Stance**: Essay supporting the position
   - **Against Stance**: Essay opposing the position
   - **Podcast**: Interactive script and audio recording

6. Download the generated content using the download buttons

## Project Structure

```
for_my_wife/
├── app.py                  # Main Streamlit application
├── debate_research_workflow.py  # Research functionality
├── podcast_script_generator.py  # Script generation
├── podcast_audio_recorder.py    # Audio recording
├── debate_illustrator.py        # Illustration generation
├── samples/                # Sample debate podcasts and outputs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

### Core Dependencies

- **streamlit**: Web application framework for creating interactive data apps
- **openai**: OpenAI API client for accessing OpenAI and Azure OpenAI models
- **python-dotenv**: Library for loading environment variables from .env files

### Research and AI Components

- **tavily-python**: API client for Tavily search engine, enabling web research capabilities
- **llama-index-core**: Core functionality for building AI applications with custom data
- **llama-index-llms-azure-openai**: Integration with Azure OpenAI for language models
- **pydantic**: Data validation and settings management using Python type annotations

### Audio and Speech Components

- **azure-cognitiveservices-speech**: Azure Speech Services SDK for text-to-speech and speech recognition

### Utility Libraries

- **requests**: HTTP library for making API requests
- **pillow**: Python Imaging Library for image processing
- **tenacity**: Retry library for handling transient failures in API calls


## Acknowledgments

- Created with love to help make informed decisions easier
- Inspired by the need to save time on research for decision-making


## Vision and Future

This app is not just a fun app, it is a step towards broadly capable AI systems not merely providing us with information, but guiding us to informed decisions. This system adapts to any domain, be it PERSONAL FINANCE, LIFESTYLE, EDUCATION, MARKETING, TECHNOLOGY, and so on. It could be used to assist not just personal, but professional use cases.

There are several next steps I have for this app, including:
- Personalisation with user chat history and preferences.
- Directly immersing the user into the debate.  
- A panel of multiple AI experts instead of just 2 AI researchers.

There are endless opportunities.

## Contact

For questions or feedback, please open an issue in the GitHub repository.
