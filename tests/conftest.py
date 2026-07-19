import pytest
from src.state import VideoIntent, ImageAnalysis

@pytest.fixture
def sample_state():
    """Provides a sample PipelineState for testing."""
    return {
        "image_folder": "data/input_images",
        "user_prompt": "Cinematic wedding reel",
        "video_intent": VideoIntent(
            pacing="slow",
            visual_style="cinematic",
            caption_tone="minimal",
            transition_preference="crossfade",
            raw_prompt="Cinematic wedding reel"
        ),
        "image_analyses": [
            ImageAnalysis(
                image_path="data/input_images/AHD_6008.jpg",
                description="Bride smiling",
                tags=["bride", "wedding", "happy"],
                quality_score=0.9
            ),
            ImageAnalysis(
                image_path="data/input_images/AHD_6106.jpg",
                description="Wedding rings close up",
                tags=["rings", "wedding", "details"],
                quality_score=0.85
            ),
            ImageAnalysis(
                image_path="data/input_images/DSC_4491.jpg",
                description="Couple dancing",
                tags=["dance", "couple", "reception"],
                quality_score=0.95
            )
        ],
        "storyboard": None,
        "remotion_script": None,
        "compile_errors": [],
        "retry_count": 0,
        "max_retries": 3,
        "render_success": False,
        "final_output_path": None,
        "failure_reason": None
    }
