import streamlit as st
import asyncio
from debate_research_workflow import research_debate_topic
from podcast_script_generator import generate_podcast_script
from podcast_audio_recorder import PodcastAudioRecorder
from debate_illustrator import generate_debate_illustration

# Configure page
st.set_page_config(
    page_title="For My Wife",
    page_icon="👩💚",
    menu_items={
        'About': "For My Wife: Multi-agentic research system that helps my wife (and anyone else) gain multifaceted insights and make informed decisions on any problem."
    }
)

# Add instructions to sidebar
with st.sidebar:
    st.markdown("# For My Wife 👩💚")
    
    # Add the wife_thinking.png image to the sidebar
    st.image("wife_thinking.png", caption="My wife thinking about decisions", use_column_width=True)
    
    # Put the "How it works" section inside a toggle
    with st.expander("ℹ️ How it works", expanded=False):
        st.markdown("""
        1. Enter any topic you need to research for decision-making
        2. The system will:
           - Analyze the topic and identify clear opposing stances
           - Generate a custom illustration of the debate scene
           - Perform targeted research for each stance
           - Generate well-structured essays supporting each position
           - Create a podcast script with a moderator and two debaters
           - Generate audio using different voices for each speaker
        3. View the results in the tabs above:
           - For Stance: Essay supporting the position
           - Against Stance: Essay opposing the position
           - Podcast: Interactive script and audio recording
        4. Download options:
           - Debate illustration
           - Podcast script in JSON format
           - Audio recording in WAV format
        """)

st.title("For My Wife 👩💚")
st.write("### 🤖🧑‍🔬️ AI researchers fight to help my wife (and you) making informed decisions on any topic")
st.markdown("My wife takes a long time before making any life decisions, whether it is to try on new diet or to get a new pair of shoes. Thorough research is a must and hasty impulsive purchases are not tolerated. I know she is not alone.")
st.markdown('''**For My Wife** is a multi-agentic research system designed to help my wife (or anyone else) gain multifaceted insights and make informed decisions on any topic. The app uses AI to generate comprehensive debates between AI researchers, providing balanced perspectives on any subject matter. This debate format is intended to deliver the researched insights in an engaging and memorable manner to people who enjoy watching dramas like my wife (I mean the users).''')
# Input section

# Input section
topic = st.text_input("🔍 Enter a Research Topic for Debate:", "Should I follow the keto diet?")
generate_button = st.button("Fight!!! 🥊", use_container_width=True)

# Create status containers
status_area = st.empty()
progress_text = ""

def update_status(message):
    global progress_text
    progress_text += f"{message}\n"
    status_area.code(progress_text)

# Create placeholder for the illustration
illustration_placeholder = st.empty()

# Create placeholder for tabs
tabs_placeholder = st.empty()

if generate_button:
    try:
        # First generate the research to get stance summaries
        update_status(f"🔍 Starting research on topic: {topic}")
        result = asyncio.run(research_debate_topic(topic))
        update_status("✅ Research complete and essays generated")
        
        # Generate and display illustration immediately
        update_status("🎨 Creating debate illustration...")
        illustration_path = asyncio.run(generate_debate_illustration(
            topic=topic,
            for_stance="",  # Not needed
            against_stance=""  # Not needed
        ))
        if illustration_path:
            illustration_placeholder.image(illustration_path, caption="Debate Scene Illustration", use_container_width=True)
            update_status("✅ Debate illustration created")
        
        # Generate remaining content
        update_status("📝 Generating podcast script...")
        script_data = asyncio.run(generate_podcast_script(
            topic=topic,
            for_essay=result["for"]["essay"],
            against_essay=result["against"]["essay"]
        ))
        update_status("✅ Podcast script generated")
        
        update_status("🎙 Generating audio recording...")
        recorder = PodcastAudioRecorder()
        audio_path = asyncio.run(recorder.generate_podcast_audio(script_data))
        update_status("✅ Audio recording complete")
        
        # Display results in tabs
        with tabs_placeholder.container():
            tab1, tab2, tab3 = st.tabs(["👍 For Stance", "👎 Against Stance", "🎧 Podcast"])
            
            with tab1:
                st.markdown(result["for"]["essay"])
                st.markdown("## 📚 References")
                for i, url in enumerate(result["for"]["references"], 1):
                    st.markdown(f"{i}. {url}")
                    
            with tab2:
                st.markdown(result["against"]["essay"])
                st.markdown("## 📚 References")
                for i, url in enumerate(result["against"]["references"], 1):
                    st.markdown(f"{i}. {url}")
            
            with tab3:
                st.markdown("## 🎧 Podcast Audio")
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/wav")
                
                st.markdown("## 📜 Podcast Script")
                for entry in script_data["dialogue"]:
                    st.markdown(f"**[{entry['role']}]**: {entry['text']}")
                
                # Download buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="📄 Download Script (JSON)",
                        data=script_data["dialogue"].__str__(),
                        file_name=f"{topic.replace(' ', '_').lower()}_podcast_script.json",
                        mime="application/json"
                    )
                with col2:
                    with open(audio_path, "rb") as f:
                        st.download_button(
                            label="🎵 Download Audio (WAV)",
                            data=f,
                            file_name=f"{topic.replace(' ', '_').lower()}_podcast.wav",
                            mime="audio/wav"
                        )
                with col3:
                    with open(illustration_path, "rb") as f:
                        st.download_button(
                            label="🖼️ Download Illustration (PNG)",
                            data=f,
                            file_name=f"{topic.replace(' ', '_').lower()}_illustration.png",
                            mime="image/png"
                        )
        
        update_status("✨ All processing complete!")
        
    except Exception as e:
        update_status(f"⚠️ Error: {str(e)}")
        st.error(f"An error occurred: {str(e)}") 