import os
from mutagen.mp3 import MP3
from pydub import AudioSegment

# Directory containing the audio files if directory does not exist create it
# audio_dir = "audio_segments"

audio_dir = "audio_segments"

if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Load all .mp3 files in order from the audio_segments folder
audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")]
audio_files.sort()  # Ensure files are sorted alphabetically/numerically

# Function to combine .mp3 files without using pydub or ffmpeg
def combine_audio_files(audio_files, output_file, intro_music_path=None):
    """Combine multiple MP3 files into a single file using PyDub."""
    if not audio_files and not intro_music_path:
        print("No audio files to combine.")
        return

    try:
        # Initialize the combined audio
        combined = None
        
        # Add intro music if provided
        if intro_music_path and os.path.exists(intro_music_path):
            try:
                print(f"Adding intro music: {intro_music_path}")
                intro_audio = AudioSegment.from_mp3(intro_music_path)
                combined = intro_audio
                print(f"Intro duration: {len(intro_audio)/1000:.2f} seconds")
            except Exception as e:
                print(f"Error processing intro music {intro_music_path}: {e}")
                combined = None

        # Process each audio file
        for audio_file in audio_files:
            try:
                # Load the audio file
                print(f"Processing file: {audio_file}")
                segment = AudioSegment.from_mp3(audio_file)
                print(f"Segment duration: {len(segment)/1000:.2f} seconds")
                
                # Add to combined audio
                if combined is None:
                    combined = segment
                else:
                    combined += segment
                    
            except Exception as e:
                print(f"Error processing file {audio_file}: {e}")
                continue

        # Export the final combined audio if we have any content
        if combined is not None:
            print(f"Exporting combined audio (total duration: {len(combined)/1000:.2f} seconds)")
            combined.export(output_file, format="mp3")
            print(f"Combined audio saved as '{output_file}'")
        else:
            print("No audio content to save")
            
    except Exception as e:
        print(f"Error combining audio files: {e}")

# Combine all audio files into a single MP3 file
if audio_files:
    print("Combining audio files...")
    combine_audio_files(audio_files, "final_podcast.mp3")
    # remove the audio segements from folder
    for audio_file in audio_files:
        # remove all audio files
        os.remove(audio_file)
    print("Audio segments moved to ARCHIVE folder.")
        
else:
    print("No valid audio segments were generated or found.")
