# from vertexai.preview.vision_models import ImageGenerationModel, Image as Vertex_Image
# from bannerBackground.load_model import get_bytes_from_pil, display_images_in_grid  # Uncomment if needed
import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel
import random

PROJECT_ID = "gentle-nuance-433709-h1"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}
vertexai.init(project=PROJECT_ID, location=LOCATION)


model = GenerativeModel("gemini-1.5-pro-002")

response_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "attribute": {
                "type": "string",
            },
        },
        "required": ["attribute"],
    },
}

def generate(theme: str):
    print("in generate here")
    response = model.generate_content(
        # f"List the 4 most important objects to tell a 5 year old to describe {theme} in one word, Do not to include human elements, Make Sure to use simple english words. Do not use words of emotions.",
        f"List the 6 most important objects to add to a banner {theme} in one word, Do not to include human elements, Make Sure to use simple english words. Do not use words of emotions.",

        generation_config=GenerationConfig(
            response_mime_type="application/json", response_schema=response_schema
        ),
    )
    print("response here: ", response.text)
    attribute_list = []
    for i in response.text[1:-2].split(','):
        attribute_list.append(list(eval(i).values())[0])
    attribute_list = sorted(attribute_list, key=lambda k: random.random())
    attribute_string = ", ".join(attribute_list)
    return attribute_string