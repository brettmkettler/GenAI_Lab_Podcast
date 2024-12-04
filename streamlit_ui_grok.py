
######################################################
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> source venv/bin/activate   
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run app.py

import streamlit as st
import os
import re
import requests
import io
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import generate_script_grok_xai
import combine

# Try to import PyPDF2, if not available, try pypdf
try:
    import PyPDF2
    pdf_reader = PyPDF2.PdfReader
except ImportError:
    try:
        from pypdf import PdfReader as pdf_reader
    except ImportError:
        st.error("Please install PyPDF2 or pypdf using: pip install PyPDF2 or pip install pypdf")
        st.stop()

# Load environment variables
load_dotenv()

# Initialize session state variables
if 'script_content' not in st.session_state:
    st.session_state.script_content = ""
if 'generated_audio' not in st.session_state:
    st.session_state.generated_audio = None

# Directory to store temporary audio files
output_dir = "audio_segments"
os.makedirs(output_dir, exist_ok=True)

def read_pdf(pdf_file):
    reader = pdf_reader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_txt(txt_file):
    return txt_file.getvalue().decode("utf-8")

def extract_youtube_transcript(video_url):
    try:
        # Extract video ID from URL
        if "youtube.com" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_url:
            video_id = video_url.split("/")[-1]
        else:
            return "Invalid YouTube URL"

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error extracting transcript: {str(e)}"

def convert_text_to_speech(script_content, voice_ids):
    audio_files = []
    segment = 0

    lines = script_content.split('\n')
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        match = re.match(r'\[(.*?)\]\s*-\s*(?:\((.*?)\))?(.*)', line.strip())
        if match:
            speaker, action, text = match.groups()
            text = text.strip().strip('"')

            if action:
                text = f"({action}) " + text

            if speaker in voice_ids:
                voice_id = voice_ids[speaker]
                output_mp3_file = os.path.join(output_dir, f"segment_{segment:03}.mp3")

                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": st.session_state.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2", 
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 1.0,
                            "style": 0.0,
                            "use_speaker_boost": True
                        }
                    }
                )

                if response.status_code == 200:
                    with open(output_mp3_file, "wb") as audio_file:
                        audio_file.write(response.content)
                    audio_files.append(output_mp3_file)
                    segment += 1

    return audio_files

def main():
    st.title("GenAI Lab - Podcast Generator (Grok X.AI)")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Content Input", "Host Configuration"])
    
    with tab1:
        st.header("Content Input")
        
        # Episode Topic Configuration
        st.subheader("Episode Topic")
        episode_topic = st.text_input("Main Topic", 
            placeholder="Enter the main topic of discussion for this episode",
            help="This is the primary topic that the hosts will discuss")
        
        additional_details = st.text_area("Additional Details (Optional)", 
            placeholder="Add any specific angles, questions, or points you want the hosts to cover",
            help="You can provide additional context, specific questions, or aspects you want the hosts to address")
        
        # Store topic information in session state
        if episode_topic:
            st.session_state.episode_topic = episode_topic
        if additional_details:
            st.session_state.additional_details = additional_details
        
        st.divider()  # Add a visual separator
        
        # Reference Materials
        st.subheader("Reference Materials")
        
        # Newsletter document upload
        st.markdown("##### Document Upload")
        uploaded_file = st.file_uploader("Upload TXT or PDF file", type=['txt', 'pdf'])
        
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                document_content = read_pdf(uploaded_file)
            else:
                document_content = read_txt(uploaded_file)
            st.session_state.document_content = document_content
            
        # YouTube URL input
        st.markdown("##### YouTube Reference")
        youtube_url = st.text_input("Enter YouTube Video URL", 
            help="The transcript will be extracted and used as additional reference material")
    
    with tab2:
        st.header("Host Configuration")
        
        # ElevenLabs API Key
        st.session_state.api_key = st.text_input("ElevenLabs API Key", type="password", value=os.getenv("ELEVENLABS_API_KEY"))
        
        # Host 1 Configuration
        st.subheader("Host 1 Configuration")
        host1_voice_id = st.text_input("Host 1 Voice ID", value="7eFTSJ6WtWd9VCU4ZlI1")
        host1_name = st.text_input("Host 1 Name", value="Brett Kettler")
        host1_bio = st.text_area("Host 1 Bio", value="He is the husband of Kimber and works in the Generative AI Laboratory with Robert Engels and Mark Roberts")
        host1_personality = st.text_area("Host 1 Personality Traits", value="Dry sense of humor, loves to talk about AI")
        
        # Host 2 Configuration
        st.subheader("Host 2 Configuration")
        host2_voice_id = st.text_input("Host 2 Voice ID", value="fQ74DTbwd8TiAJFxu9v8")
        host2_name = st.text_input("Host 2 Name", value="Kimber Kettler")
        host2_bio = st.text_area("Host 2 Bio", value="Kimber is the wife of Brett and teaches yoga.")
        host2_personality = st.text_area("Host 2 Personality Traits", value="Curious about AI and the world, loves to ask questions")
        
        # Generate Script Button
        if st.button("Generate Script"):
            if 'document_content' in st.session_state:
                # Combine document content and YouTube transcript if available
                research_content = st.session_state.document_content
                if 'youtube_transcript' in st.session_state:
                    research_content += "\n" + st.session_state.youtube_transcript
                
                # Check if all required fields are filled
                if not all([host1_name, host1_bio, host1_personality, 
                           host2_name, host2_bio, host2_personality]):
                    st.error("Please fill in all host information before generating the script.")
                    return
                
                with st.spinner("Generating podcast script..."):
                    try:
                        # Generate script using updated generate_script_oai function
                        topic = "Discussion of the newsletter content"
                        st.session_state.script_content = generate_script_grok_xai.generate_response(
                            topic=topic,
                            relevant_docs=research_content,
                            host1_name=host1_name,
                            host1_bio=host1_bio,
                            host1_personality=host1_personality,
                            host2_name=host2_name,
                            host2_bio=host2_bio,
                            host2_personality=host2_personality
                        )
                        st.success("Script generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating script: {str(e)}")
            else:
                st.error("Please upload a document or provide a YouTube URL first.")
                
        # Display and edit script
        if st.session_state.script_content:
            st.subheader("Edit Script")
            edited_script = st.text_area(
                "Edit the generated script below:",
                value=st.session_state.script_content,
                height=400
            )
            st.session_state.script_content = edited_script
            
            # Generate Podcast Button
            if st.button("Generate Podcast"):
                if st.session_state.api_key:
                    voice_ids = {
                        host1_name: host1_voice_id,
                        host2_name: host2_voice_id
                    }
                    
                    with st.spinner("Generating podcast audio..."):
                        # Convert script to speech
                        audio_files = convert_text_to_speech(edited_script, voice_ids)
                        
                        if audio_files:
                            # Combine audio files
                            final_audio = "final_podcast.mp3"
                            combine.combine_audio_files(audio_files, final_audio)
                            
                            # Clean up individual audio files
                            for audio_file in audio_files:
                                os.remove(audio_file)
                            
                            # Save the final audio to session state
                            with open(final_audio, "rb") as f:
                                st.session_state.generated_audio = f.read()
                            
                            # Display audio player and download button
                            st.audio(st.session_state.generated_audio, format="audio/mp3")
                            st.download_button(
                                label="Download Podcast",
                                data=st.session_state.generated_audio,
                                file_name="podcast.mp3",
                                mime="audio/mp3"
                            )
                else:
                    st.error("Please enter your ElevenLabs API key")

if __name__ == "__main__":
    main()