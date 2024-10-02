from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import subprocess
import bannerBackground
from bannerBackground.bannergen import bannerBackground
import os

app = FastAPI()

# Define a request model for validation, but we won't use it directly
class BannerRequest(BaseModel):
    prodImg: str
    theme: str
    colPal: str
    proMo: str
    network_pkl: str
    bg: str
    bg_preprocessing: str
    strings: str
    string_labels: str
    outfile: str
    out_postprocessing: str

# Default values for form parameters
DEFAULTS = {
    "network_pkl": "checkpoints/layoutdetr_ad_banner.pkl",
    "bg": "examples/generated_image_0.png",
    "bg_preprocessing": "256",
    "strings": "EVERYTHING 10% OFF|Friends & Family Savings Event|SHOP NOW|CODE FRIEND10",
    "string_labels": "header|body text|button|disclaimer / footnote",
    "outfile": "examples/output/bannerOutput2",
    "out_postprocessing": "horizontal_center_aligned"
}

def run_generate_command(request: BannerRequest):

    bannerbackground = bannerBackground(theme=request.theme, prodImg=request.prodImg)
    bcgImg = bannerbackground.getBannerBackground()
    print("bcgImg", bcgImg)
    request.bg = bcgImg

    # Construct the command as a list of arguments
    command = [
        "python", "generate.py",
        f"--ckpt={request.network_pkl}",
        f"--bg={request.bg}",
        f"--bg-preprocessing={request.bg_preprocessing}",
        f"--strings={request.strings}",
        f"--string-labels={request.string_labels}",
        f"--outfile={request.outfile}",
        f"--out-postprocessing={request.out_postprocessing}",
    ]
    
    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)

    return result.stdout

@app.post("/generate/")
async def generate_banner(
    prodImg: str = Form(),
    theme: str = Form(),
    colPal: str = Form(),
    proMo: str = Form(),
    network_pkl: str = Form(DEFAULTS["network_pkl"]),
    bg: str = Form(DEFAULTS["bg"]),
    bg_preprocessing: str = Form(DEFAULTS["bg_preprocessing"]),
    strings: str = Form(DEFAULTS["strings"]),
    string_labels: str = Form(DEFAULTS["string_labels"]),
    outfile: str = Form(DEFAULTS["outfile"]),
    out_postprocessing: str = Form(DEFAULTS["out_postprocessing"])
):
    request = BannerRequest(
        prodImg = prodImg,
        theme = theme,
        colPal = colPal,
        proMo = proMo,
        network_pkl=network_pkl,
        bg=bg,
        bg_preprocessing=bg_preprocessing,
        strings=strings,
        string_labels=string_labels,
        outfile=outfile,
        out_postprocessing=out_postprocessing
    )
    
    try:
        output = run_generate_command(request)
        return {"message": "Banner generation done"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
