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

                    DO NOT USE MARKUP IN THE SCRIPT.
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    You are writing a Podcast type of general discussion between two hosts, 
                    {host1_name} and {host2_name}. The conversation should be extremely casual conversation with a lot of back and forth.
                    They will talk back and forth and make it very natural speech.

                    Create a 15 minute podcast script for the next episode of "AI Futures Lab Visionary Bytes" where {host1_name} and {host2_name} discuss the topics below with as much detail as possible:

                    {topic}

                    Here are some relevant research documents to consider:
                    {relevant_docs}

                    CONSIDERATIONS:
                    - Keep the conversation responses short and concise and more back and forth.
                    - Keep the conversation engaging and informative.
                    - Make speakers laugh by saying "ha hahaha" or "haha", DO NOT USE (laughs)
                    - They can say "um" or "uh" or "hmm" if thinking or pausing.
                    - They can ask each other questions or make comments about things they find interesting.
                    - They can make jokes or puns.
                    - They can use casual language or slang.
                    - They can interrupt each other.
                    - They can agree or disagree with each other.

                    RESPONSES:
                    - They can respond in one or 5 word sentences and make the script longer if needed.
                    - Include natural conversational interjections like "oh" or "yeah" are fine.
                    - Do a full deep dive and analysis of the topic with back and forth conversation.

                    FORMAT FOR THE SCRIPT:
                    [{host1_name}] - "Text to be spoken."
                    [{host2_name}] - "Text to be spoken."

                    Use this exact format for the script.
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