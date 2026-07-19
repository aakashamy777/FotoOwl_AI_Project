import time
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import PipelineState
from src.rag_store import get_retriever

load_dotenv()

# We choose gemini-2.5-pro over flash here because generating correct, compilable React/TSX
# code with complex Remotion Sequence timings and transitions requires advanced coding reasoning.
# The quality trade-off of using a pro-tier model is necessary for zero compilation errors.

class ScriptOutput(BaseModel):
    """Pydantic schema to enforce structured code generation output from the LLM."""
    code: str

def script_generator(state: PipelineState) -> PipelineState:
    """Retrieve relevant Remotion snippets via RAG and generate a complete TSX composition code."""
    intent = state.get("video_intent")
    storyboard = state.get("storyboard")
    
    if not intent or not storyboard:
        print("Error: Missing video_intent or storyboard in state.")
        return state

    try:
        # Retrieve Remotion snippets relevant to the transition preference and workflow
        retriever = get_retriever("remotion_snippets", k=4)
        query = f"{intent.transition_preference} sequence image caption transition"
        docs = retriever.invoke(query)
        api_context = "\n\n".join([doc.page_content for doc in docs])

        # If compile errors exist, fetch the most relevant snippet to fix it
        errors = state.get("compile_errors", [])
        if errors:
            latest_error = errors[-1]
            error_query = latest_error.error_message
            err_docs = retriever.invoke(error_query)
            err_context = "\n\n".join([d.page_content for d in err_docs])
            api_context = (
                f"### PREVIOUS ERROR TO FIX:\n"
                f"Error Type: {latest_error.error_type}\n"
                f"Error Message: {latest_error.error_message}\n\n"
                f"### Relevance Snippet for Fixing:\n{err_context}\n\n"
                f"{api_context}"
            )

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(ScriptOutput)

        # Build detailed prompt with storyboard and intent instructions
        scenes_info = []
        for scene in storyboard.scenes:
            scenes_info.append(
                f"Scene {scene.scene_id}:\n"
                f"  Image Path: {scene.image_path}\n"
                f"  Caption: {scene.caption}\n"
                f"  Duration: {scene.duration_seconds}s\n"
                f"  Transition: {scene.transition_type}\n"
            )
        scenes_context = "\n".join(scenes_info)

        system_instruction = (
            "You are an expert Remotion developer. Generate a complete, self-contained TSX component "
            "named 'EventReel' that renders a video matching the storyboard and intent guidelines below.\n\n"
            "### Remotion API Reference Snippets (RAG):\n"
            f"{api_context}\n\n"
            "Requirements:\n"
            "- Define the main component: export const EventReel = () => { ... }\n"
            "- It must use TransitionSeries from '@remotion/transitions' to orchestrate scenes and transitions.\n"
            "- Render each scene inside TransitionSeries.Sequence using Img with a slow zoom/Ken Burns scale animation.\n"
            "- Render the caption text over the image using useCurrentFrame() and interpolate() to fade it in and out.\n"
            "- Transition types and durations must match the storyboard description (e.g., fade, slide, etc.).\n"
            "- In TransitionSeries, transitions overlap adjacent sequences. Total duration in frames is: "
            "total_duration_frames = sum(scene_duration_frames) - (num_scenes - 1) * transition_duration_frames.\n"
            "- Frame rate is 30 FPS. Ensure all imports are correct, including staticFile if loading assets.\n"
            "- Output ONLY valid, compilable TypeScript React (TSX) code. No markdown wrapping."
        )

        user_content = (
            f"### Video Intent:\n"
            f"- pacing: {intent.pacing}\n"
            f"- visual_style: {intent.visual_style}\n"
            f"- caption_tone: {intent.caption_tone}\n"
            f"- transition_preference: {intent.transition_preference}\n\n"
            f"### Storyboard scenes:\n{scenes_context}\n"
            f"### Total Duration: {storyboard.total_duration_seconds}s"
        )

        # Retry loop for 429 rate limit errors (max 2 attempts)
        max_attempts = 2
        result = None
        for attempt in range(max_attempts):
            try:
                result = structured_llm.invoke([
                    ("system", system_instruction),
                    ("user", user_content)
                ])
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_attempts - 1:
                        sleep_time = 35
                        print(f"Rate limited. Retrying in {sleep_time}s... (Attempt {attempt+1}/{max_attempts})")
                        time.sleep(sleep_time)
                        continue
                raise e

        if result:
            state["remotion_script"] = result.code
    except Exception as e:
        print(f"Warning: Script generation failed: {e}")
        state["remotion_script"] = None
        
    return state

if __name__ == "__main__":
    from src.state import VideoIntent, Storyboard, StoryboardScene
    
    # Define manually configured test state
    test_intent = VideoIntent(
        pacing="slow",
        visual_style="cinematic",
        caption_tone="minimal",
        transition_preference="crossfade",
        raw_prompt="Cinematic wedding reel"
    )
    
    test_storyboard = Storyboard(
        scenes=[
            StoryboardScene(
                scene_id=1,
                image_path="data/input_images/AHD_6008.jpg",
                caption="A beautiful beginning...",
                duration_seconds=3.0,
                transition_type="crossfade"
            ),
            StoryboardScene(
                scene_id=2,
                image_path="data/input_images/AHD_6106.jpg",
                caption="Celebrated with family.",
                duration_seconds=3.0,
                transition_type="crossfade"
            )
        ],
        total_duration_seconds=6.0
    )
    
    test_state = {
        "image_folder": "data/input_images",
        "user_prompt": "Cinematic wedding reel",
        "video_intent": test_intent,
        "image_analyses": [],
        "storyboard": test_storyboard,
        "remotion_script": None,
        "compile_errors": [],
        "retry_count": 0,
        "max_retries": 3,
        "render_success": False,
        "final_output_path": None,
        "failure_reason": None
    }
    
    print("Running script generator test...")
    test_state = script_generator(test_state)
    
    code = test_state["remotion_script"]
    if code:
        print("\n=== Generated Remotion Code ===")
        print(code)
    else:
        print("\nError: No code generated.")
