from bannerBackground.generatePrompt import generate
from bannerBackground.getBackgroundBanner import generate_and_save_image

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
        generated_images_paths = generate_and_save_image(PROMPT, self.prodImg,
                                                        save_path_prefix=GENERATED_IMAGE_PATH_PREFIX)
        print("generated images: ", generated_images_paths)
        return generated_images_paths[0]