import pytest
from unittest.mock import MagicMock, patch
from src.nodes.intent_parser import intent_parser
from src.state import VideoIntent

def test_intent_parser_cinematic():
    """Test intent_parser with cinematic requirements."""
    mock_intent = VideoIntent(
        pacing="slow",
        visual_style="cinematic",
        caption_tone="minimal",
        transition_preference="crossfade",
        raw_prompt="Cinematic wedding reel"
    )
    
    state = {
        "user_prompt": "Cinematic wedding reel, slow and emotional",
        "video_intent": None
    }
    
    with patch("src.nodes.intent_parser.ChatGoogleGenerativeAI") as mock_chat:
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_chat.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = mock_intent
        
        result_state = intent_parser(state)
        
        assert result_state["video_intent"] is not None
        assert result_state["video_intent"].visual_style == "cinematic"
        assert result_state["video_intent"].pacing == "slow"

def test_intent_parser_upbeat():
    """Test intent_parser with upbeat requirements."""
    mock_intent = VideoIntent(
        pacing="fast",
        visual_style="upbeat",
        caption_tone="bold",
        transition_preference="slide",
        raw_prompt="Fast upbeat birthday video"
    )
    
    state = {
        "user_prompt": "Fast upbeat birthday video",
        "video_intent": None
    }
    
    with patch("src.nodes.intent_parser.ChatGoogleGenerativeAI") as mock_chat:
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_chat.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured
        mock_structured.invoke.return_value = mock_intent
        
        result_state = intent_parser(state)
        
        assert result_state["video_intent"] is not None
        assert result_state["video_intent"].visual_style == "upbeat"
        assert result_state["video_intent"].transition_preference == "slide"
