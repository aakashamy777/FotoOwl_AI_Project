from typing import Literal, TypedDict
from pydantic import BaseModel

class VideoIntent(BaseModel):
    """Structured intent representation parsed from a user's prompt."""
    pacing: Literal["slow", "medium", "fast"]
    visual_style: Literal["cinematic", "upbeat", "corporate"]
    caption_tone: Literal["minimal", "bold", "professional"]
    transition_preference: Literal["crossfade", "hard_cut", "slide"]
    raw_prompt: str

class ImageAnalysis(BaseModel):
    """Vision analysis results for an uploaded image."""
    image_path: str
    description: str
    tags: list[str]
    quality_score: float

class StoryboardScene(BaseModel):
    """Details of a single scene in the video storyboard."""
    scene_id: int
    image_path: str
    caption: str
    duration_seconds: float
    transition_type: str

class Storyboard(BaseModel):
    """Full video storyboard composed of sequentially ordered scenes."""
    scenes: list[StoryboardScene]
    total_duration_seconds: float

class CompileError(BaseModel):
    """Compilation error information captured from Remotion."""
    error_message: str
    error_type: str

class PipelineState(TypedDict):
    """Shared state dictionary representing the LangGraph pipeline execution state."""
    image_folder: str
    user_prompt: str
    video_intent: VideoIntent | None
    image_analyses: list[ImageAnalysis]
    storyboard: Storyboard | None
    remotion_script: str | None
    compile_errors: list[CompileError]
    retry_count: int
    max_retries: int
    render_success: bool
    final_output_path: str | None
    failure_reason: str | None
