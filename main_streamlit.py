import streamlit as st
import os
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi

from dotenv import load_dotenv
import generate_script_oai
import combine

# Load environment variables
load_dotenv()

# Your ElevenLabs API key
API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Define the voice IDs for each host
voice_ids = {
    "Brett": "nPczCjzI2devNBz1zQrb",  # Replace with Brett's voice_id
    "Kimber": "vvGvpdg3szmd4HufhYMg"  # Replace with Kimber's voice_id
}

# Directory to store temporary audio files
output_dir = "audio_segments"
os.makedirs(output_dir, exist_ok=True)

# Function to convert text to speech using ElevenLabs API and save as MP3
def convert_text_to_speech(script_file):
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.readlines()

    audio_files = []
    segment = 0  # Start segment numbering from 0

    for i, line in enumerate(script_content):
        match = re.match(r'\[(.*?)\]\s*-\s*(?:\((.*?)\))?(.*)', line.strip())

        if match:
            speaker, action, text = match.groups()
            text = text.strip().strip('"')  # Remove surrounding quotes if any

            if action:
                text = f"({action}) " + text  # Add the action before the text

            if speaker in voice_ids:
                voice_id = voice_ids[speaker]

                # Output file for this segment in .mp3 format with leading zeros in the file name
                output_mp3_file = os.path.join(output_dir, f"segment_{segment:03}.mp3")

                # Prepare the API call
                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={
                        "xi-api-key": API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "voice_settings": {
                            "stability": 0.1,
                            "similarity_boost": 0.3,
                            "style": 0.2
                        }
                    }
                )

                # Check for valid response content
                if response.status_code == 200 and response.headers.get("Content-Type") == "audio/mpeg":
                    # Write the audio data to the .mp3 file
                    with open(output_mp3_file, "wb") as audio_file:
                        audio_file.write(response.content)

                    audio_files.append(output_mp3_file)
                    segment += 1

    return audio_files

# Function to generate podcast from YouTube video and topic
def generate_podcast(video_id, topic):
    try:
        # Fetch transcript
        relevant_research = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in relevant_research])

        # Save the transcript
        os.makedirs("RESEARCH", exist_ok=True)
        transcript_file = f"RESEARCH/{topic}.txt"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Generate podcast script
        script_file = "podcast_script.txt"
        generate_script_oai.write_script_to_file(generate_script_oai.generate_response(topic, transcript_text))

        # Convert script to speech
        audio_files = convert_text_to_speech(script_file)

        # Combine audio files
        final_audio = "final_podcast.mp3"
        combine.combine_audio_files(audio_files, final_audio)

        # Cleanup audio segments
        for audio_file in audio_files:
            os.remove(audio_file)

        return final_audio

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Streamlit app layout
st.title("Podcast Generator")

# User inputs
video_id = st.text_input("YouTube Video ID", value="Q055E67zHXk")
topic = st.text_input("Podcast Topic", value="90 Day Fiance Rayne and Chidi live in alternate realities")

# Generate podcast button
if st.button("Generate Podcast"):
    with st.spinner("Generating podcast..."):
        final_audio = generate_podcast(video_id, topic)

        if final_audio:
            st.success("Podcast generated successfully!")
            st.audio(final_audio)
            with open(final_audio, "rb") as f:
                st.download_button(label="Download Podcast", data=f, file_name=final_audio, mime="audio/mpeg")
