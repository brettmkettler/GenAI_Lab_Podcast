import os
from mutagen.mp3 import MP3
from pydub import AudioSegment

# Directory containing the audio files if directory does not exist create it
audio_dir = "audio_segments"

if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

def combine_audio_files(audio_files, output_file, intro_music_path=None):
    """
    Combine audio files with optional intro music using pydub.
    
    Args:
        audio_files (list): List of audio file paths to combine
        output_file (str): Path for the output combined file
        intro_music_path (str, optional): Path to the intro music file
    """
    # Check if the list of audio files is empty
    if not audio_files and not intro_music_path:
        print("No audio files to combine.")
        return

    try:
        # Initialize combined audio
        combined = None

        # First, add the intro music if provided
        if intro_music_path and os.path.exists(intro_music_path):
            try:
                print(f"Adding intro music: {intro_music_path}")
                # Load intro music based on file type
                if intro_music_path.lower().endswith('.wav'):
                    intro = AudioSegment.from_wav(intro_music_path)
                elif intro_music_path.lower().endswith('.mp3'):
                    intro = AudioSegment.from_mp3(intro_music_path)
                else:
                    raise ValueError("Unsupported intro music format")
                
                combined = intro
            except Exception as e:
                print(f"Error processing intro music {intro_music_path}: {e}")

        # Then add all the speech segments
        for audio_file in audio_files:
            try:
                print(f"Adding file: {audio_file}")
                # Load the audio segment
                segment = AudioSegment.from_mp3(audio_file)
                
                # If this is the first audio file and no intro music
                if combined is None:
                    combined = segment
                else:
                    combined += segment
                    
            except Exception as e:
                print(f"Error processing file {audio_file}: {e}")
                continue

        if combined:
            # Export the final combined audio
            combined.export(output_file, format="mp3")
            print(f"Combined audio saved as '{output_file}'")
        else:
            print("No audio was combined.")
            
    except Exception as e:
        print(f"Error combining audio files: {e}")
        raise e

# Function to list all audio files in order
def get_audio_files():
    if not os.path.exists(audio_dir):
        return []
    audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    return sorted(audio_files)  # Ensure files are sorted alphabetically/numerically