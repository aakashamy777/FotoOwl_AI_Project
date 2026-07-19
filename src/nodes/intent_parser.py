import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import PipelineState, VideoIntent

load_dotenv()

def intent_parser(state: PipelineState) -> PipelineState:
    """Parse the user's free-text video generation prompt into a structured VideoIntent object."""
    user_prompt = state.get("user_prompt", "")
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(VideoIntent)
        
        system_instruction = (
            "You are an AI assistant parsing video generation requirements. "
            "Map the user prompt to these exact allowed values:\n"
            "- pacing: 'slow', 'medium', or 'fast'\n"
            "- visual_style: 'cinematic', 'upbeat', or 'corporate'\n"
            "- caption_tone: 'minimal', 'bold', or 'professional'\n"
            "- transition_preference: 'crossfade', 'hard_cut', or 'slide'\n"
            "Also populate the raw_prompt field with the input user prompt."
        )
        
        messages = [
            ("system", system_instruction),
            ("user", user_prompt)
        ]
        
        # Retry loop for 429 rate limit errors (max 2 attempts)
        max_attempts = 2
        result = None
        for attempt in range(max_attempts):
            try:
                result = structured_llm.invoke(messages)
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < max_attempts - 1:
                        sleep_time = 3 if attempt == 0 else 6
                        print(f"Rate limited. Retrying in {sleep_time}s... (Attempt {attempt+1}/{max_attempts})")
                        time.sleep(sleep_time)
                        continue
                raise e
                
        # Ensure raw_prompt is correctly set
        if result and hasattr(result, "raw_prompt"):
            result.raw_prompt = user_prompt
        state["video_intent"] = result
    except Exception as e:
        print(f"Warning: Intent parsing failed: {e}. Falling back to default VideoIntent.")
        state["video_intent"] = VideoIntent(
            pacing="medium",
            visual_style="cinematic",
            caption_tone="minimal",
            transition_preference="crossfade",
            raw_prompt=user_prompt
        )
    return state

if __name__ == "__main__":
    # Test cases
    test_state_1 = {
        "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones, minimal text",
        "video_intent": None
    }
    test_state_2 = {
        "user_prompt": "Upbeat birthday reel, fast cuts, bold captions, energetic",
        "video_intent": None
    }
    
    print("Testing prompt 1...")
    res_1 = intent_parser(test_state_1)
    print("Result 1:", res_1["video_intent"])
    
    print("\nTesting prompt 2...")
    res_2 = intent_parser(test_state_2)
    print("Result 2:", res_2["video_intent"])
