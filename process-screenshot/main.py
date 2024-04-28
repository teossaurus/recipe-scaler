# import base64
# import vertexai
# from vertexai.generative_models import GenerativeModel, Part, FinishReason
# import vertexai.preview.generative_models as generative_models
import functions_framework
import json

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


# GENERATION_CONFIG = {
#     "max_output_tokens": 8192,
#     "temperature": 0,
#     "top_p": 0.95,
# }

# SAFETY_SETTINGS = {
#     generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
#     generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
#     generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
#     generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
# }

# def generate(prompt, images):
#     vertexai.init(project="recipe-scaler-421622", location="us-west1")
#     model = GenerativeModel("gemini-1.5-pro-preview-0409")


#     combined_inputs = images + [Part.from_text(prompt)]


#     responses = model.generate_content(
#         combined_inputs,
#         generation_config=GENERATION_CONFIG,
#         safety_settings=SAFETY_SETTINGS,
#     )

#     for c in responses.candidates:
#         print(c.content)

# def prep_images(images):
#     images = images.split(",") if "," in images else [images]
#     prepped_images = []
#     for i in images:
#         data = base64.b64decode(i)
#         d = Part.from_data(mime_type="image/png", data=data)
#         prepped_images.append(d)

#     return prepped_images


def generate(prompt, image_urls):
    import os

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
            ]
            + [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                    },
                }
                for url in image_urls
            ],
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
    )
    res = response.choices[0].message.content
    return clean_up_response(res)


def prep_images(images):
    images = images.split(",") if "," in images else [images]
    images = [f"http:{i}" for i in images]
    return images


@functions_framework.http
def handler(request):
    data = request.get_json()
    images = data["images"]
    prepped_images = prep_images(images)
    prompt = get_prompt()
    recipe = generate(prompt, prepped_images)

    return json.dumps(recipe), 200
