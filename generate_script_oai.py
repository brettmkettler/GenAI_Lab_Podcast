import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(topic, relevant_docs, host1_name, host1_bio, host1_personality, host2_name, host2_bio, host2_personality):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a script writer for a podcast called "The AI Experiment". 

                PERSONALITIES:

                {host1_name}: 
                Bio: {host1_bio}
                Personality: {host1_personality}

                {host2_name}:
                Bio: {host2_bio}
                Personality: {host2_personality}

                DO NOT USE ** OR ANY OTHER MARKUP IN THE SCRIPT.
                """
            },
            {
                "role": "user",
                "content": f"""
                You are writing a Podcast type of general discussion between two hosts, 
                {host1_name} and {host2_name}. The conversation should be extremely casual conversation with a lot of back and forth.
                They will talk back and forth and make it very natural speech.

                Create a 5 minute podcast script for the next episode of "The AI Experiment" where {host1_name} and {host2_name} discuss the topics below:

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

                FORMAT FOR THE SCRIPT:
                [{host1_name}] - "Text to be spoken."
                [{host2_name}] - "Text to be spoken."

                DO NOT USE ** OR ANY OTHER MARKUP IN THE SCRIPT.
                """
            }
        ],
        model="gpt-4",
    )

    return chat_completion.choices[0].message.content

def write_script_to_file(script_text):
    with open("podcast_script.txt", "w", encoding="utf-8") as f:
        f.write(script_text)
    print("Script written to podcast_script.txt")