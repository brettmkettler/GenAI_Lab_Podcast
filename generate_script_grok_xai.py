import json
import os
import requests
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("X.AI API key not found in environment variables")

# API Configuration
API_URL = "https://api.x.ai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {XAI_API_KEY}"
}

def generate_response(topic, relevant_docs, host1_name, host1_bio, host1_personality, 
                     host2_name, host2_bio, host2_personality):
    """
    Generate a podcast script using the X.AI API with direct requests.
    """
    try:
        print(f"Starting script generation for topic: {topic[:100]}...")

        # Prepare the request payload
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                    You are a script writer for a podcast called "AI Futures Lab Visionary Bytes". 

                    PERSONALITIES:

                    {host1_name}: 
                    Bio: {host1_bio}
                    Personality: {host1_personality}

                    {host2_name}:
                    Bio: {host2_bio}
                    Personality: {host2_personality}

                    IMPORTANT FORMATTING RULES:
                    1. DO NOT USE ANY MARKUP like **, __, or other special characters
                    2. DO NOT USE PARENTHESES FOR ACTIONS
                    3. ONLY USE PLAIN TEXT IN THE DIALOGUE
                    4. FOLLOW THE EXACT FORMAT SHOWN BELOW
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Write a natural, casual podcast conversation between {host1_name} and {host2_name}.
                    The conversation should flow naturally with lots of back and forth dialogue.

                    TOPIC:
                    {topic}

                    REFERENCE MATERIALS:
                    {relevant_docs}

                    CONVERSATION STYLE:
                    - Keep responses short and conversational
                    - Use natural speech patterns
                    - Include casual reactions like "hmm", "oh", "yeah"
                    - Show laughter with "haha" or "ha ha"
                    - Allow for interruptions and overlapping dialogue
                    - Mix in questions and comments
                    - Keep it engaging and informative
                    - Use casual language and slang when appropriate

                    SCRIPT FORMAT:
                    [{host1_name}] - "Spoken text here"
                    [{host2_name}] - "Spoken text here"

                    IMPORTANT:
                    1. DO NOT USE ** or any other markup characters
                    2. DO NOT USE (parentheses) for actions
                    3. ONLY USE PLAIN TEXT in the dialogue
                    4. EXACTLY follow the format above with square brackets and quotes
                    """
                }
            ],
            "model": "grok-beta",
            "stream": False,
            "temperature": 0.7
        }

        # Make the API request
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=payload,
            verify=False  # Skip SSL verification
        )

        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        script = result['choices'][0]['message']['content']
        
        # Write the script to file
        write_script_to_file(script)
        
        return script

    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error in script generation: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise Exception(error_msg)

def write_script_to_file(script_text):
    """
    Write the generated script to a file.
    """
    try:
        with open("podcast_script.txt", "w", encoding="utf-8") as f:
            f.write(script_text)
        print("Successfully wrote script to podcast_script.txt")
    except Exception as e:
        error_msg = f"Error writing script to file: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise Exception(error_msg)

def test_api_connection():
    """
    Test the connection to the X.AI API.
    """
    try:
        test_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Test connection"
                }
            ],
            "model": "grok-beta",
            "max_tokens": 5,
            "stream": False
        }
        
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json=test_payload,
            verify=False
        )
        
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"API connection test failed: {str(e)}")
        return False

# Test API connection on module import
if __name__ == "__main__":
    if test_api_connection():
        print("X.AI API connection successful")
    else:
        print("Failed to connect to X.AI API")