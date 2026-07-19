import os
import base64
import glob
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import PipelineState, ImageAnalysis

load_dotenv()

# We choose gemini-2.5-flash over a pro-tier model here because this step runs
# once per image (12+ calls in sequence/parallel) and needs to be fast and
# cost-effective, which gemini-2.5-flash achieves while supporting excellent vision capability.

def encode_image(image_path: str) -> str:
    """Helper function to base64 encode an image file."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def image_analyser(state: PipelineState) -> PipelineState:
    """Analyze all images in the input directory and append their analyses to the state."""
    folder = state.get("image_folder", "")
    if not os.path.exists(folder):
        print(f"Error: image_folder '{folder}' does not exist.")
        return state

    # Get all supported image files sorted alphabetically
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(folder, ext)))
    image_paths = sorted(list(set(image_paths)))

    if "image_analyses" not in state or state["image_analyses"] is None:
        state["image_analyses"] = []

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(ImageAnalysis)

    for path in image_paths:
        try:
            b64_data = encode_image(path)
            # Determine image MIME subtype
            ext = os.path.splitext(path)[1].lower().strip(".")
            mime_type = "jpeg" if ext in ("jpg", "jpeg") else ext
            
            prompt = (
                "Provide a short description of the image, list relevant tags "
                "(subjects, settings, mood, lighting), and evaluate its visual "
                "quality_score between 0 and 1."
            )
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{mime_type};base64,{b64_data}"}
                    }
                ]
            )
            
            res = structured_llm.invoke([message])
            if res:
                res.image_path = path
                state["image_analyses"].append(res)
                print(f"Analyzed {os.path.basename(path)} successfully.")
        except Exception as e:
            print(f"Warning: Failed to analyze image '{path}': {e}")
            
    return state

if __name__ == "__main__":
    # Test script block
    test_state = {
        "image_folder": "data/input_images",
        "image_analyses": []
    }
    print("Starting batch image analysis test...")
    result_state = image_analyser(test_state)
    print("\nBatch analysis completed. Results:")
    for analysis in result_state.get("image_analyses", []):
        print(f"- Path: {analysis.image_path}")
        print(f"  Description: {analysis.description}")
        print(f"  Tags: {analysis.tags}")
        print(f"  Quality Score: {analysis.quality_score:.2f}")
