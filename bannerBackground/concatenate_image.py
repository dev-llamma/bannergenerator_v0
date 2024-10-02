
from PIL import Image

def concatenate_images(image_paths, output_path, top_padding=50, between_image_padding=10):
    print("in concatenate image")
    """
    Concatenates images side by side with asymmetric padding, suitable for a banner.
    
    :param image_paths: List of image file paths to concatenate.
    :param output_path: File path to save the concatenated image.
    :param top_padding: Padding at the top of the banner.
    :param between_image_padding: Padding between the images.
    """
    # Calculate other padding values (half of top_padding)
    side_padding = top_padding // 2
    bottom_padding = top_padding // 2

    # Load all images, convert to RGBA to preserve transparency if necessary
    images = [Image.open(image_path).convert("RGBA") for image_path in image_paths]
    
    # Find the total width and max height for the new image
    total_width = sum(image.width for image in images) + between_image_padding * (len(images) - 1)
    max_height = max(image.height for image in images)
    
    # Add padding to the width and height
    final_width = total_width + 2 * side_padding
    final_height = max_height + top_padding + bottom_padding
    
    # Create a new image with a transparent background to hold the concatenated result
    concatenated_image = Image.new('RGBA', (final_width, final_height), (255, 255, 255, 0))  # White transparent background
    
    # Calculate the starting x position to center the images horizontally
    x_offset = side_padding
    
    # Paste each image into the new image, aligned by the bottom edge with edge padding
    for img in images:
        # Calculate the y_offset to align the image with the bottom, considering top padding
        y_offset = final_height - img.height - bottom_padding
        
        # Paste the image into the concatenated image
        concatenated_image.paste(img, (x_offset, y_offset), mask=img)  # Use the image itself as a mask to preserve transparency
        x_offset += img.width + between_image_padding
    
    # Convert to RGB if saving as a non-transparent format (e.g., JPEG) or keep as RGBA for PNG
    if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
        concatenated_image = concatenated_image.convert("RGB")  # Convert to RGB to discard alpha for JPEG
    
    # Save the concatenated image
    concatenated_image.save(output_path)
    print(f"Image saved to {output_path}")
    return output_path

