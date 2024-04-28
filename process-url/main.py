# Standard library imports
import os
import json
import requests
from requests.exceptions import RequestException



# Third party imports
import functions_framework
import html2text
from openai import OpenAI

def get_prompt(file_path="prompt.txt"):
    with open(file_path, "r") as f:
        prompt = f.read()
    return prompt

def clean_up_response(response_content):
    if response_content.startswith("```json") and response_content.endswith("```"):
        r = response_content.replace("```json", "").replace("```", "")
        
    else:
        r = response_content

    r = r.strip()
    return json.loads(r)

def generate(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
    )
    res = response.choices[0].message.content
    return clean_up_response(res)

# write function that calls a url that's taken as an argument and returns the html
def get_webpage_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        text = html2text.html2text(response.text)
        print(len(text.split(" ")));
        return text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve HTML: {e}")
        return ""

@functions_framework.http
def handler(request):
    data = request.get_json()
    url = data["url"]
    text = get_webpage_text_from_url(url)
    prompt = get_prompt()
    prompt_with_text = prompt.replace("<recipe_website_text/>", "<recipe_website_text>" + text + "</recipe_website_text>")
    chatgpt_response = generate(prompt_with_text)
    return chatgpt_response
