from bannerBackground.generatePrompt import generate
from bannerBackground.getBackgroundBanner import generate_and_save_image
from bannerBackground.concatenate_image import concatenate_images
import glob

# image_paths = ['40085808.png', '20000540.png', '189909.png']  # Replace with actual image paths


GENERATED_IMAGE_PATH_PREFIX = 'generated_image'
class bannerBackground:

    def __init__(self, theme, prodImg):
        self.theme = theme
        self.prodImg = prodImg
        return None
    
    def getBannerBackground(self):
        print("in generating background banner")
        # PROMPT = "Lights, Fireworks, Candles, Night, Goodness"
        PROMPT = generate(self.theme)
        # image_paths = list(self.prodImg)
        # image_paths = glob.glob('test_images/*')
        # print(image_paths)
        print("prodImg input",self.prodImg)
        if ',' in self.prodImg:
            image_paths = self.prodImg.split(',')
            output_path = str(self.prodImg).split(',')[0]+ '_concatenated_image.png' 
        else: 
            image_paths = self.prodImg
            output_path = self.prodImg+'_concatenated_image.png'

        tem_int_image =concatenate_images(image_paths, output_path, top_padding=500, between_image_padding=10)

        generated_images_paths = generate_and_save_image(PROMPT, tem_int_image,
                                                        save_path_prefix=GENERATED_IMAGE_PATH_PREFIX)
        print("generated images: ", generated_images_paths)
        return generated_images_paths[0]