# AI Lab Podcast Generator

A powerful application that generates AI-driven podcast conversations using Grok X.AI for script generation and ElevenLabs for voice synthesis. This tool creates natural-sounding discussions between two AI hosts about any topic you choose.

## Features

- 🎙️ **Dynamic Script Generation**: Uses Grok X.AI to create natural, engaging dialogue between two hosts
- 🗣️ **Voice Synthesis**: Leverages ElevenLabs for high-quality voice generation
- 🎵 **Custom Intro Music**: Support for default or custom intro music
- 📚 **Multiple Input Sources**: 
  - Direct topic input
  - PDF document upload
  - Text file upload
  - YouTube video transcript extraction
- 👥 **Customizable Hosts**: Configure host names, personalities, and voices
- 🎧 **Audio Processing**: Combines all audio segments with intro music

## Prerequisites

- Python 3.11 or higher
- Virtual environment (recommended)
- Required API Keys:
  - X.AI API Key (for script generation)
  - ElevenLabs API Key (for voice synthesis)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI_Lab_Podcast
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables in a `.env` file:
```env
XAI_API_KEY=your_xai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run streamlit_ui_grok.py
```

2. Navigate to the web interface (typically http://localhost:8501)

3. Configure your podcast:
   - **Content Input Tab**:
     - Enter the main topic and additional details
     - Upload reference materials (PDF/TXT) or provide YouTube URLs
     - Choose or upload intro music
   
   - **Host Configuration Tab**:
     - Enter your ElevenLabs API key
     - Configure host names, voices, and personalities
     - Click "Generate Podcast" to create your content

4. The application will:
   - Generate a natural conversation script
   - Convert the script to audio using the selected voices
   - Combine all audio segments with intro music
   - Provide the final podcast for playback and download

## File Structure

- `streamlit_ui_grok.py`: Main Streamlit interface
- `generate_script_grok_xai.py`: Script generation using X.AI
- `combine.py`: Audio processing and combination
- `requirements.txt`: Python dependencies
- `IntroCapgemini.mp3`: Default intro music
- `audio_segments/`: Temporary storage for audio segments

## Voice Configuration

Default voice IDs:
- Host 1: "7eFTSJ6WtWd9VCU4ZlI1" (Brett)
- Host 2: "fQ74DTbwd8TiAJFxu9v8" (Kimber)

You can replace these with any valid ElevenLabs voice ID.

## Dependencies

Main dependencies include:
- streamlit
- python-dotenv
- elevenlabs
- groq
- pydub
- youtube-transcript-api
- mutagen
- PyPDF2

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Failed API requests
- Invalid file uploads
- Audio processing issues
- Missing dependencies

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Specify your license here]

## Acknowledgments

- Grok X.AI for natural language processing
- ElevenLabs for voice synthesis
- Streamlit for the web interface

## Support

For support, please [specify contact method or create an issue in the repository].
