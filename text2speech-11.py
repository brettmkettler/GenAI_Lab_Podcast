import requests
import re
import os
from pydub import AudioSegment
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

import ARCHIVE.generate_script as generate_script
import combine

import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Your ElevenLabs API key
API_KEY = os.getenv("ELEVENLABS_API_KEY")




######################



# Define the voice IDs for each host
voice_ids = {
    "Brett": "JSGwt4dfzg0ANnLeNSUH",  # Replace with Brett's voice_id
    "Kimber": "fQ74DTbwd8TiAJFxu9v8"  # Replace with Kimber's voice_id
}



##########################



# Directory to store temporary audio files
output_dir = "audio_segments"
os.makedirs(output_dir, exist_ok=True)

# 11labs API
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(line: str, output_mp3_file: str, segment: str, speaker: str, voice_id: str, text: str) -> str:
    # Calling the text_to_speech conversion API with detailed parameters
    response = client.text_to_speech.convert(
        voice_id=voice_id, 
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2", # use the turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )


    # Writing the audio to a file
    with open(output_mp3_file, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"Processed line {line}: '{text}' by {speaker}")

    # Return the path of the saved audio file
    return output_mp3_file


# Function to convert text to speech using ElevenLabs API and save as MP3
def convert_text_to_speech(script_file):
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.readlines()

    audio_files = []
    segment = 0  # Start segment numbering from 0

    print("Processing podcast script...")

    # Process each line in the script file
    try:
        
        for i, line in enumerate(script_content):
            match = re.match(r'\[(.*?)\]\s*[–-]\s*(?:\((.*?)\))?(.*)', line.strip())


            if match:
                speaker, action, text = match.groups()
                text = text.strip().strip('"')  # Remove surrounding quotes if any

                if action:
                    text = f"({action}) " + text  # Add the action before the text
                

                if speaker in voice_ids:
                    voice_id = voice_ids[speaker]
                    
                    print(f"Voice ID: {voice_id}")
                    
                    

                    # Output file for this segment in .mp3 format with leading zeros in the file name
                    output_mp3_file = os.path.join(output_dir, f"segment_{segment:03}.mp3")

                    response = text_to_speech_file(line, output_mp3_file, segment, speaker, voice_id, text)
                    
                    #add +1 line
                    line = i + 1
                    
                    segment += 1
                    
                    if response:
                        print(f"Audio saved as '{response}'")
                
            else:
                print(f"Error processing line {i+1}: Invalid format")

        

    except Exception as e:
        print(f"An error occurred: {e}")

######################################################
# Main Script






# Provide the path to your podcast script file
convert_text_to_speech("podcast_script.txt")


# Combine all audio segments into a single MP3 file
# Directory containing the audio files
audio_dir = "audio_segments"

# Load all .mp3 files in order from the audio_segments folder
audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")]
audio_files.sort()  # Ensure files are sorted alphabetically/numerically



# Combine all audio files into a single MP3 file
if audio_files:
    print("Combining audio files...")
    combine.combine_audio_files(audio_files, "final_podcast.mp3")
    # remove the audio segements from folder
    for audio_file in audio_files:
        # remove all audio files
        os.remove(audio_file)
    print(f"Final podcast audio saved as 'final_podcast.mp3'")
