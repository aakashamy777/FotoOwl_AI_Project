from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import PipelineState, Storyboard, StoryboardScene
from src.rag_store import get_retriever

load_dotenv()

# We choose gemini-2.5-flash here because storyboard writing is a structured
# sequencing task that requires mid-tier reasoning (matching images, pacing, and
# style guides to form a narrative arc) rather than full creative TSX script generation.

def storyboard_writer(state: PipelineState) -> PipelineState:
    """Select the best subset of images and sequence them into a narrative storyboard using RAG style guides."""
    intent = state.get("video_intent")
    analyses = state.get("image_analyses", [])
    
    if not intent:
        print("Error: No video intent found in state.")
        return state

    try:
        # Retrieve style guide chunks using RAG
        retriever = get_retriever("style_guides", k=3)
        query = f"{intent.visual_style} style pacing captions transitions"
        docs = retriever.invoke(query)
        style_context = "\n\n".join([doc.page_content for doc in docs])

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(Storyboard)

        # Prepare images context for prompt
        images_info = []
        for i, img in enumerate(analyses):
            images_info.append(
                f"Image {i+1}:\n"
                f"Path: {img.image_path}\n"
                f"Description: {img.description}\n"
                f"Tags: {', '.join(img.tags)}\n"
                f"Quality Score: {img.quality_score}\n"
            )
        images_context = "\n".join(images_info)

        system_instruction = (
            "You are an expert video director. Your job is to select the best subset of images and sequence them "
            "into a coherent narrative storyboard. Use the retrieved style guide context below to guide your choices "
            "for pacing, caption tone, and transitions.\n\n"
            f"### Style Guide Context:\n{style_context}\n\n"
            "Guidelines:\n"
            f"- Pacing preference: pacing={intent.pacing}\n"
            f"- Visual style: visual_style={intent.visual_style}\n"
            f"- Caption tone: caption_tone={intent.caption_tone}\n"
            f"- Transition preference: transition_preference={intent.transition_preference}\n"
            "- Select only the most relevant, high-quality images that tell a logical story. Do not use all images if they don't fit.\n"
            "- Sequence them to form an emotional/logical beginning, middle, and end.\n"
            "- Set scene duration_seconds and transition_type (e.g. 'crossfade', 'slide', 'hard_cut') per scene, matching preferences.\n"
            "- Compute and set total_duration_seconds as the sum of all scenes' duration_seconds."
        )

        user_content = f"Here is the pool of analyzed images:\n\n{images_context}"
        
        result = structured_llm.invoke([
            ("system", system_instruction),
            ("user", user_content)
        ])
        state["storyboard"] = result
    except Exception as e:
        print(f"Warning: Storyboard writing failed: {e}. Building fallback storyboard.")
        fallback_scenes = []
        subset = analyses[:5] if len(analyses) >= 5 else analyses
        for idx, img in enumerate(subset):
            fallback_scenes.append(
                StoryboardScene(
                    scene_id=idx + 1,
                    image_path=img.image_path,
                    caption="",
                    duration_seconds=3.0,
                    transition_type="crossfade"
                )
            )
        state["storyboard"] = Storyboard(
            scenes=fallback_scenes,
            total_duration_seconds=len(fallback_scenes) * 3.0
        )
    return state

if __name__ == "__main__":
    from src.nodes.intent_parser import intent_parser
    from src.nodes.image_analyser import image_analyser

    test_state = {
        "image_folder": "data/input_images",
        "user_prompt": "Cinematic wedding reel, slow and emotional, warm tones, minimal text",
        "image_analyses": [],
        "video_intent": None,
        "storyboard": None
    }
    
    print("Step 1: Running image analyser...")
    test_state = image_analyser(test_state)
    
    print("\nStep 2: Running intent parser...")
    test_state = intent_parser(test_state)
    
    print("\nStep 3: Running storyboard writer...")
    test_state = storyboard_writer(test_state)
    
    sb = test_state["storyboard"]
    if sb:
        print("\n=== Storyboard Created ===")
        print(f"Total Duration: {sb.total_duration_seconds} seconds")
        print(f"Number of Scenes: {len(sb.scenes)}")
        for scene in sb.scenes:
            print(f"\nScene {scene.scene_id}:")
            print(f"  Image: {scene.image_path}")
            print(f"  Caption: '{scene.caption}'")
            print(f"  Duration: {scene.duration_seconds}s")
            print(f"  Transition: {scene.transition_type}")
    else:
        print("\nError: No storyboard returned.")
