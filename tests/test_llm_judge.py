import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from src.state import Storyboard, StoryboardScene

class NarrativeCoherenceJudge(BaseModel):
    """Pydantic model representing LLM-as-a-judge score structure."""
    coherence_score: int
    reasoning: str

def run_coherence_judge(storyboard: Storyboard) -> NarrativeCoherenceJudge:
    """LLM-as-a-judge function evaluating storyboard narrative coherence."""
    import langchain_google_genai
    llm = langchain_google_genai.ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(NarrativeCoherenceJudge)
    
    scenes_text = "\n".join([f"- Scene {s.scene_id}: {s.caption}" for s in storyboard.scenes])
    prompt = f"Evaluate the narrative coherence of this storyboard script:\n{scenes_text}"
    
    return structured_llm.invoke(prompt)

def test_coherence_judge_success():
    """Test LLM-as-a-judge evaluations correctly interpret coherence score thresholds."""
    storyboard = Storyboard(
        scenes=[
            StoryboardScene(
                scene_id=1,
                image_path="data/input_images/AHD_6008.jpg",
                caption="A beautiful bride prepares for her wedding.",
                duration_seconds=3.0,
                transition_type="crossfade"
            ),
            StoryboardScene(
                scene_id=2,
                image_path="data/input_images/DSC_4491.jpg",
                caption="The newlywed couple dances at the reception.",
                duration_seconds=3.0,
                transition_type="crossfade"
            )
        ],
        total_duration_seconds=6.0
    )
    
    mock_judge_response = NarrativeCoherenceJudge(
        coherence_score=8,
        reasoning="Good chronological sequencing of wedding stages (preparation to reception)."
    )
    
    with patch("langchain_google_genai.ChatGoogleGenerativeAI") as mock_chat:
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_chat.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = mock_judge_response
        
        result = run_coherence_judge(storyboard)
        
        assert result.coherence_score > 5
        assert "chronological" in result.reasoning.lower()
