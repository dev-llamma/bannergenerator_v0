# @title Import libraries
# @markdown Run this cell before proceeding to import libraries and define utility functions. \
# @markdown You will also load the imagegeneration@006 model from the Vertex AI SDK.

import io
import math
from typing import Any

from PIL import Image
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from vertexai.preview.vision_models import Image as Vertex_Image
from vertexai.preview.vision_models import ImageGenerationModel, ImageGenerationResponse


# Gets the image bytes from a PIL Image object.
def get_bytes_from_pil(image: Image) -> bytes:
    byte_io_png = io.BytesIO()
    image.save(byte_io_png, "PNG")
    return byte_io_png.getvalue()


# Corrects the orientation of an image if needed. Uses the EXIF tag 274
# to check if an image has been rotated and if so, reverts it.
def maybe_rotate(img_pil: Image):
    exif = img_pil.getexif()
    rotation = exif.get(274)

    if rotation == 3:
        img_pil = img_pil.rotate(180, expand=True)
    elif rotation == 6:
        img_pil = img_pil.rotate(270, expand=True)
    elif rotation == 8:
        img_pil = img_pil.rotate(90, expand=True)
    return img_pil


# Extract bounding boxes from a mask.
def get_b_box_from_mask(
    mask_image: np.ndarray, box_area_threshold: int = 50
) -> np.ndarray:
    contours, _ = cv.findContours(mask_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    b_boxes = np.zeros((len(contours), 4))
    for i, contour in enumerate(contours):
        x, y, w, h = cv.boundingRect(contour)
        b_boxes[i] = (x, y, x + w, y + h)
    b_boxes = filter(
        lambda x: (x[2] - x[0]) * (x[3] - x[1]) > box_area_threshold, b_boxes
    )
    b_boxes = sorted(b_boxes, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)
    return b_boxes


# Edits specific areas and pastes them back into the original image.
def crop_insert_paste(
    generation_model: ImageGenerationModel,
    image: Image,
    mask: Image,
    boxes: np.array,
    pad_ratio: int,
    prompt: str,
    neg_prompt: str,
    seed: int = 0,
    mask_dilation: float = 0.01,
    guidance_scale: int = 60,
    samples: int = 4,
):
    generated_imgs = [image.copy() for _ in range(samples)]
    for box in boxes:
        # Calculate cropping area with padding.
        box_w_pad = pad_ratio * (box[2] - box[0])
        box_h_pad = pad_ratio * (box[3] - box[1])
        x1 = np.round(np.clip(box[0] - box_w_pad, 0, image.width)).astype("int")
        x2 = np.round(np.clip(box[2] + box_w_pad, 0, image.width)).astype("int")
        y1 = np.round(np.clip(box[1] - box_h_pad, 0, image.height)).astype("int")
        y2 = np.round(np.clip(box[3] + box_h_pad, 0, image.height)).astype("int")

        im_crop = image.crop([x1, y1, x2, y2])
        mask_crop = mask.crop([x1, y1, x2, y2])
        image_vertex = Vertex_Image(image_bytes=get_bytes_from_pil(im_crop))
        mask_vertex = Vertex_Image(image_bytes=get_bytes_from_pil(mask_crop))

        # Edit the cropped area of the image.
        generated_crops = generation_model.edit_image(
            prompt=prompt,
            negative_prompt=neg_prompt,
            base_image=image_vertex,
            mask=mask_vertex,
            number_of_images=samples,
            edit_mode="inpainting-insert",
            seed=seed,
            guidance_scale=guidance_scale,
            mask_dilation=mask_dilation,
        )

        # Paste the generated edits of the cropped area into the corresponding
        # positions in the base image.
        for i, crop in enumerate(generated_crops.images):
            generated_imgs[i].paste(crop._pil_image, (x1, y1))
    return generated_imgs


# Pads an image for outpainting. Provides options to control the positioning of
# the original image.
def pad_to_target_size(
    source_image,
    target_size=(1536, 1536),
    mode="RGB",
    vertical_offset_ratio=0,
    horizontal_offset_ratio=0,
    fill_val=255,
):
    orig_image_size_w, orig_image_size_h = source_image.size
    target_size_w, target_size_h = target_size

    insert_pt_x = (target_size_w - orig_image_size_w) // 2 + int(
        horizontal_offset_ratio * target_size_w
    )
    insert_pt_y = (target_size_h - orig_image_size_h) // 2 + int(
        vertical_offset_ratio * target_size_h
    )
    insert_pt_x = min(insert_pt_x, target_size_w - orig_image_size_w)
    insert_pt_y = min(insert_pt_y, target_size_h - orig_image_size_h)

    if mode == "RGB":
        source_image_padded = Image.new(
            mode, target_size, color=(fill_val, fill_val, fill_val)
        )
    elif mode == "L":
        source_image_padded = Image.new(mode, target_size, color=(fill_val))
    else:
        raise ValueError("source image mode must be RGB or L.")

    source_image_padded.paste(source_image, (insert_pt_x, insert_pt_y))
    return source_image_padded


# Pads and resizes image and mask to the same target size.
def pad_image_and_mask(
    image_vertex: Vertex_Image,
    mask_vertex: Vertex_Image,
    target_size,
    vertical_offset_ratio,
    horizontal_offset_ratio,
    viz=True,
):
    image_vertex.thumbnail(target_size)
    mask_vertex.thumbnail(target_size)

    image_vertex = pad_to_target_size(
        image_vertex,
        target_size=target_size,
        mode="RGB",
        vertical_offset_ratio=vertical_offset_ratio,
        horizontal_offset_ratio=horizontal_offset_ratio,
        fill_val=0,
    )
    mask_vertex = pad_to_target_size(
        mask_vertex,
        target_size=target_size,
        mode="L",
        vertical_offset_ratio=vertical_offset_ratio,
        horizontal_offset_ratio=horizontal_offset_ratio,
        fill_val=255,
    )
    if viz:
        print(
            f"image size(with x height): {image_vertex.size[0]} x {image_vertex.size[1]}"
        )
        plt.axis("off")
        plt.imshow(image_vertex)
        plt.imshow(mask_vertex, alpha=0.3)
        plt.title("Padded image and mask overlay")
    return image_vertex, mask_vertex


# Displays images in a grid below the cell
def display_images_in_grid(images: []) -> None:
    """Displays the provided images in a grid format. 4 images per row.

    Args:
        images: A list of images to display.
    """

    # Determine the number of rows and columns for the grid layout.
    nrows: int = math.ceil(len(images) / 4)  # Display at most 4 images per row
    ncols: int = min(len(images) + 1, 4)  # Adjust columns based on the number of images

    # Create a figure and axes for the grid layout.
    _, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 6))

    for i, ax in enumerate(axes.flat):
        if i < len(images):
            # Display the image in the current axis.
            if hasattr(images[i], "_pil_image"):
                image = images[i]._pil_image
                image.save('temp.jpg')
            else:
                image = images[i]
            ax.imshow(image)

            # Adjust the axis aspect ratio to maintain image proportions.
            ax.set_aspect("equal")

            # Disable axis ticks for a cleaner appearance.
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            # Hide empty subplots to avoid displaying blank axes.
            ax.axis("off")

    # Adjust the layout to minimize whitespace between subplots.
    plt.tight_layout()

    # Display the figure with the arranged images.
    # plt.show()