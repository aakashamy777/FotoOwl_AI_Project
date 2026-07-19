from typing import Literal
import pytest
from src.graph import route_after_compile
from src.state import CompileError

def test_route_after_compile_success():
    """Test routing when compilation succeeds (render_success is True)."""
    state = {
        "compile_errors": [CompileError(error_message="earlier error", error_type="compile_error")],
        "render_success": True,
        "retry_count": 0,
        "max_retries": 3
    }
    assert route_after_compile(state) == "render"

def test_route_after_compile_retry():
    """Test routing when compilation fails and retry limit is not exceeded."""
    state = {
        "compile_errors": [CompileError(error_message="failed to build", error_type="compile_error")],
        "render_success": False,
        "retry_count": 1,
        "max_retries": 3
    }
    assert route_after_compile(state) == "retry"

def test_route_after_compile_fail():
    """Test routing when compilation fails and retry limit is exceeded."""
    state = {
        "compile_errors": [CompileError(error_message="failed to build", error_type="compile_error")],
        "render_success": False,
        "retry_count": 3,
        "max_retries": 3
    }
    assert route_after_compile(state) == "fail"
