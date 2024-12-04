import requests
import re
import os
from pydub import AudioSegment
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

import combine

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
                            "model": "eleven_multilingual_v2",
                            "voice_settings": {
                                "stability": 0.5,
                                "similarity_boost": 0.75,
                                "style": 0.0,
                                "use_speaker_boost": True
                            }
                        }
                    )
                

                    # Check for valid response content
                    if response.status_code == 200 and response.headers.get("Content-Type") == "audio/mpeg":
                        # Write the audio data to the .mp3 file
                        with open(output_mp3_file, "wb") as audio_file:
                            audio_file.write(response.content)

                        audio_files.append(output_mp3_file)
                        print(f"Processed line {i+1}: '{text}' by {speaker}")
                        segment += 1
                    else:
                        print(f"Error processing line {i+1}: Status Code {response.status_code}, Message: {response.json()}")
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
