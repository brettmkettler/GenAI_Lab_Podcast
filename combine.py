import os
from mutagen.mp3 import MP3

# Directory containing the audio files if directory does not exist create it
# audio_dir = "audio_segments"

audio_dir = "audio_segments"

if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Load all .mp3 files in order from the audio_segments folder
audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")]
audio_files.sort()  # Ensure files are sorted alphabetically/numerically

# Function to combine .mp3 files without using pydub or ffmpeg
def combine_audio_files(audio_files, output_file):
    # Check if the list of audio files is empty
    if not audio_files:
        print("No audio files to combine.")
        return

    try:
        # Open the output file in binary write mode
        with open(output_file, "wb") as outfile:
            for audio_file in audio_files:
                try:
                    # Check if the file is a valid MP3
                    mp3_audio = MP3(audio_file)
                    print(f"Adding file: {audio_file}, Duration: {mp3_audio.info.length} seconds")

                    # Read and write the content of the MP3 file
                    with open(audio_file, "rb") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    print(f"Error processing file {audio_file}: {e}")
                    continue

        print(f"Combined audio saved as '{output_file}'")
    except Exception as e:
        print(f"Error exporting combined audio file: {e}")

# # Combine all audio files into a single MP3 file
# if audio_files:
#     print("Combining audio files...")
#     combine_audio_files(audio_files, "final_podcast.mp3")
#     # remove the audio segements from folder
#     for audio_file in audio_files:
#         # remove all audio files
#         os.remove(audio_file)
#     print("Audio segments moved to ARCHIVE folder.")
        
# else:
#     print("No valid audio segments were generated or found.")
