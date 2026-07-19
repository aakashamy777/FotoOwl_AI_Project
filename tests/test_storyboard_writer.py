import pytest
from unittest.mock import MagicMock, patch
from src.nodes.storyboard_writer import storyboard_writer
from src.state import Storyboard, StoryboardScene

def test_storyboard_writer(sample_state):
    """Test storyboard_writer logic and state aggregation."""
    mock_storyboard = Storyboard(
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
                image_path="data/input_images/DSC_4491.jpg",
                caption="Together, always.",
                duration_seconds=3.0,
                transition_type="crossfade"
            )
        ],
        total_duration_seconds=6.0
    )

    with patch("src.nodes.storyboard_writer.ChatGoogleGenerativeAI") as mock_chat, \
         patch("src.nodes.storyboard_writer.get_retriever") as mock_get_retriever:
        
        # Mock RAG store retriever
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever
        mock_retriever.invoke.return_value = [MagicMock(page_content="style guide content")]
        
        # Mock LLM calls
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_chat.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = mock_storyboard
        
        result_state = storyboard_writer(sample_state)
        
        assert result_state["storyboard"] is not None
        assert len(result_state["storyboard"].scenes) == 2
        assert result_state["storyboard"].total_duration_seconds == 6.0
