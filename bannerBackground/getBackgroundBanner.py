PROJECT_ID = "gentle-nuance-433709-h1"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}

import io
import math
import vertexai
from PIL import Image
import numpy as np
from vertexai.preview.vision_models import ImageGenerationModel, Image as Vertex_Image
from bannerBackground.load_model import get_bytes_from_pil, display_images_in_grid  # Uncomment if needed

vertexai.init(project=PROJECT_ID, location=LOCATION)

IMAGE_GENERATION_MODEL = "imagegeneration@006"
generation_model = ImageGenerationModel.from_pretrained(IMAGE_GENERATION_MODEL)


def generate_and_save_image(prompt, base_image_path, product_position="fixed", save_path_prefix="generated_image"):
    print(prompt)
    """
    Generates an image based on a prompt and a base image, and saves the result.

    Args:
        prompt (str): The text prompt for image generation.
        base_image_path (str): Path to the base image.
        product_position (str): Positioning of the product in the image.
        save_path_prefix (str): Prefix for saving generated images.

    Returns:
        List of generated images or an empty list if an error occurs.
    """
    try:
        # Load base image
        image_pil = Image.open(base_image_path)
        image_vertex = Vertex_Image(image_bytes = get_bytes_from_pil(image_pil))

        # Generate images
        generated_images = generation_model.edit_image(
            prompt=prompt,
            base_image=image_vertex,
            edit_mode="product-image",
            product_position=product_position,
        )

        # Save generated images
        saved_image_paths = []
        for idx, img in enumerate(generated_images.images):
            img_pil = img._pil_image if hasattr(img, "_pil_image") else img  # Ensure it's a PIL image
            save_path = f"{save_path_prefix}_{idx}.png"
            img_pil.save(save_path, format="PNG")  # Save as PNG
            saved_image_paths.append(save_path)

        generated_images = [Image.open(path) for path in saved_image_paths]
        display_images_in_grid(generated_images)  # Uncomment if needed

        return saved_image_paths

    except Exception as e:
        print(f"An error occurred: {e}")
        return []