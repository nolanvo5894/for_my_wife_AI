# For My Wife 💝

## Overview

My wife takes a long time before making any life decisions, whether it is to try on new diet or to get a new pair of shoes. Thorough research is a must and hasty impulsive purchases are not tolerated. I know she is not alone.

**For My Wife** is a multi-agentic research system designed to help my wife (or anyone else) gain multifaceted insights and make informed decisions on any topic. The app uses AI to generate comprehensive debates between AI researchers, providing balanced perspectives on any subject matter. This debate format is intended to deliver the researched insights in an engaging and memorable manner to people who enjoy watching dramas like my wife (I mean the users).

This project was created to save time on research when making decisions, offering a comprehensive understanding of topics through deep research, structured debates, visual illustrations, and audio presentations.

## Features

- **Comprehensive Research**: Analyzes topics and identifies diverse, opposing perspectives for deep research
- **Visual Debates**: Generates custom illustrations
- **Structured Essays**: Creates well-researched essays supporting each position
- **Interactive Podcasts**: Produces debate scripts with a moderator and two debaters.
- **Audio Generation**: Converts scripts to audio using different voices for each speaker
- **Downloadable Content**: Save illustrations, scripts, and audio recordings

## Screenshots

![App Screenshot](screenshots/app_screenshot.png)

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

5. Explore the results in the three tabs:
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


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Created with love to help make informed decisions easier
- Inspired by the need to save time on research for decision-making

## Contact

For questions or feedback, please open an issue in the GitHub repository.
