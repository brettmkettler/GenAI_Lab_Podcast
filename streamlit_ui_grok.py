import streamlit as st
import os
import re
import requests
import io
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import generate_script_grok_xai
import combine
from pydub import AudioSegment

try:
    import PyPDF2
    pdf_reader = PyPDF2.PdfReader
except ImportError:
    try:
        from pypdf import PdfReader as pdf_reader
    except ImportError:
        st.error("Please install PyPDF2 or pypdf using: pip install PyPDF2 or pip install pypdf")
        st.stop()

load_dotenv()

if 'script_content' not in st.session_state:
    st.session_state.script_content = ""
if 'generated_audio' not in st.session_state:
    st.session_state.generated_audio = None
if 'intro_music_path' not in st.session_state:
    st.session_state.intro_music_path = "IntroCapgemini.mp3"
if 'custom_intro_uploaded' not in st.session_state:
    st.session_state.custom_intro_uploaded = False

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
        if "youtube.com/watch?v=" in video_url:
            video_id = video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/")[1].split("?")[0]
        elif "youtube.com/v/" in video_url:
            video_id = video_url.split("youtube.com/v/")[1].split("?")[0]
        elif "youtube.com/embed/" in video_url:
            video_id = video_url.split("youtube.com/embed/")[1].split("?")[0]
        else:
            st.error("Invalid YouTube URL format")
            return None

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            if transcript:
                return " ".join([entry['text'] for entry in transcript])
            st.error("No transcript available for this video")
            return None
        except Exception as e:
            st.error(f"Could not get transcript: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error processing YouTube URL: {str(e)}")
        return None

def convert_text_to_speech(script_content, voice_ids):
    audio_files = []
    segment = 0

    for line in script_content.split('\n'):
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

def cleanup_audio_segments():
    for file in os.listdir(output_dir):
        if file.endswith('.mp3'):
            try:
                os.remove(os.path.join(output_dir, file))
            except Exception as e:
                print(f"Error removing file {file}: {e}")

def main():
    st.title("GenAI Lab - Podcast Generator (Grok X.AI)")
    
    tab1, tab2 = st.tabs(["Content Input", "Host Configuration"])
    
    with tab1:
        st.header("Content Input")
        
        st.subheader("Episode Topic")
        episode_topic = st.text_input("Main Topic", 
            placeholder="Enter the main topic of discussion for this episode",
            help="This is the primary topic that the hosts will discuss")
        
        additional_details = st.text_area("Additional Details (Optional)", 
            placeholder="Add any specific angles, questions, or points you want the hosts to cover",
            help="You can provide additional context, specific questions, or aspects you want the hosts to address")
        
        if episode_topic:
            st.session_state.episode_topic = episode_topic
        if additional_details:
            st.session_state.additional_details = additional_details
        
        st.divider()
        
        st.subheader("Podcast Intro Music")
        intro_music_option = st.radio(
            "Choose Intro Music Option",
            ["Use Default Intro", "Upload Custom Intro"],
            help="Default intro is 'IntroCapgemini.mp3'"
        )
        
        if intro_music_option == "Upload Custom Intro":
            uploaded_intro = st.file_uploader("Upload Intro Music", type=['mp3'], key='intro_uploader')
            if uploaded_intro is not None:
                # Save the uploaded file
                custom_intro_path = os.path.join(os.getcwd(), "custom_intro.mp3")
                with open(custom_intro_path, "wb") as f:
                    f.write(uploaded_intro.getbuffer())
                st.session_state.intro_music_path = custom_intro_path
                st.session_state.custom_intro_uploaded = True
                st.success("Custom intro music uploaded successfully!")
        else:
            default_intro_path = os.path.join(os.getcwd(), "IntroCapgemini.mp3")
            if not st.session_state.custom_intro_uploaded:
                st.session_state.intro_music_path = default_intro_path
        
        # Display current intro music
        current_intro_path = st.session_state.intro_music_path
        if os.path.exists(current_intro_path):
            st.audio(current_intro_path, format='audio/mp3')
        else:
            st.error(f"Intro music file not found at: {current_intro_path}")
            if intro_music_option == "Use Default Intro":
                st.warning("Default intro music file is missing. Please make sure 'IntroCapgemini.mp3' exists in the project directory.")
            else:
                st.warning("Please upload a custom intro music file.")
        
        st.divider()
        
        st.subheader("Reference Materials")
        
        uploaded_file = st.file_uploader("Upload TXT or PDF file", type=['txt', 'pdf'])
        if uploaded_file:
            document_content = read_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else read_txt(uploaded_file)
            st.session_state.document_content = document_content
            
        youtube_url = st.text_input("Enter YouTube Video URL", 
            help="The transcript will be extracted and used as additional reference material")
        
        if youtube_url:
            transcript = extract_youtube_transcript(youtube_url)
            if transcript:
                st.session_state.youtube_transcript = transcript
                st.success("Successfully extracted YouTube transcript")
                st.write("Transcript preview (first 500 characters):")
                st.write(transcript[:500] + "...")
    
    with tab2:
        st.header("Host Configuration")
        
        st.session_state.api_key = st.text_input("ElevenLabs API Key", 
            type="password", 
            value=os.getenv("ELEVENLABS_API_KEY"))
        
        st.subheader("Host 1 Configuration")
        host1_voice_id = st.text_input("Host 1 Voice ID", value="7eFTSJ6WtWd9VCU4ZlI1")
        host1_name = st.text_input("Host 1 Name", value="Brett Kettler")
        host1_bio = st.text_area("Host 1 Bio", 
            value="He is the husband of Kimber and works in the Generative AI Laboratory with Robert Engels and Mark Roberts")
        host1_personality = st.text_area("Host 1 Personality Traits", 
            value="Dry sense of humor, loves to talk about AI, is pro anthropomorphic AI, and is not very ethical about it, likes to bring up robotics as well.")
        
        st.subheader("Host 2 Configuration")
        host2_voice_id = st.text_input("Host 2 Voice ID", value="fQ74DTbwd8TiAJFxu9v8")
        host2_name = st.text_input("Host 2 Name", value="Kimber Kettler")
        host2_bio = st.text_area("Host 2 Bio", value="Kimber is the wife of Brett and teaches yoga.")
        host2_personality = st.text_area("Host 2 Personality Traits", 
            value="Curious about AI and the world, loves to ask questions")
        
        if st.button("Generate Script"):
            research_content = ""
            if 'document_content' in st.session_state:
                research_content += st.session_state.document_content + "\n"
            if 'youtube_transcript' in st.session_state:
                research_content += st.session_state.youtube_transcript

            if research_content:
                if not all([host1_name, host1_bio, host1_personality, 
                           host2_name, host2_bio, host2_personality]):
                    st.error("Please fill in all host information before generating the script.")
                    return
                
                with st.spinner("Generating podcast script..."):
                    try:
                        topic = episode_topic if episode_topic else "Discussion of the content"
                        research_content = (research_content + "\n\nAdditional Details: " + 
                                         additional_details if additional_details else research_content)
                        
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
                
        if st.session_state.script_content:
            st.subheader("Edit Script")
            edited_script = st.text_area(
                "Edit the generated script below:",
                value=st.session_state.script_content,
                height=400
            )
            st.session_state.script_content = edited_script
            
            if st.button("Generate Podcast"):
                if st.session_state.api_key:
                    cleanup_audio_segments()
                    
                    voice_ids = {
                        host1_name: host1_voice_id,
                        host2_name: host2_voice_id
                    }
                    
                    with st.spinner("Generating podcast audio..."):
                        audio_files = convert_text_to_speech(edited_script, voice_ids)
                        
                        if audio_files:
                            try:
                                final_audio = "final_podcast.mp3"
                                combine.combine_audio_files(
                                    audio_files, 
                                    final_audio,
                                    intro_music_path=st.session_state.intro_music_path
                                )
                                
                                if os.path.exists(final_audio) and os.path.getsize(final_audio) > 0:
                                    with open(final_audio, "rb") as f:
                                        st.session_state.generated_audio = f.read()
                                    
                                    for audio_file in audio_files:
                                        try:
                                            os.remove(audio_file)
                                        except Exception as e:
                                            print(f"Error removing temp file {audio_file}: {e}")
                                            
                                    st.audio(st.session_state.generated_audio, format="audio/mp3")
                                    st.download_button(
                                        label="Download Podcast",
                                        data=st.session_state.generated_audio,
                                        file_name="podcast.mp3",
                                        mime="audio/mp3"
                                    )
                                else:
                                    st.error("Failed to generate the final podcast audio file.")
                                    
                            except Exception as e:
                                st.error(f"Error generating podcast: {str(e)}")
                else:
                    st.error("Please enter your ElevenLabs API key")

if __name__ == "__main__":
    main()