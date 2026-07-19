from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.state import PipelineState

from src.nodes.intent_parser import intent_parser
from src.nodes.image_analyser import image_analyser
from src.nodes.storyboard_writer import storyboard_writer
from src.nodes.script_generator import script_generator
from src.nodes.compiler_fixer import compiler_fixer
from src.nodes.renderer import renderer

def fail_node(state: PipelineState) -> dict:
    print("Executing node: fail_node")
    return {"failure_reason": "Max compile retries reached without success."}

def increment_retry_node(state: PipelineState) -> dict:
    print("Executing node: increment_retry")
    return {"retry_count": state.get("retry_count", 0) + 1}

# Conditional routing logic
def route_after_compile(state: PipelineState) -> Literal["retry", "render", "fail"]:
    """Conditional router determining transition after the compiler_fixer.
    
    If compilation was successful (render_success is True), we route to render.
    Otherwise, if we have not exceeded max_retries (default 3), we route to retry
    which increments the retry count and routes back to script_generator.
    If retry count exceeds max_retries, we route to the terminal fail node.
    """
    if state.get("render_success", False):
        return "render"
    
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    
    if retry_count < max_retries:
        return "retry"
    else:
        return "fail"

# Define the StateGraph structure
builder = StateGraph(PipelineState)

# Add all pipeline nodes
builder.add_node("intent_parser", intent_parser)
builder.add_node("image_analyser", image_analyser)
builder.add_node("storyboard_writer", storyboard_writer)
builder.add_node("script_generator", script_generator)
builder.add_node("compiler_fixer", compiler_fixer)
builder.add_node("renderer", renderer)
builder.add_node("fail", fail_node)
builder.add_node("increment_retry", increment_retry_node)

# Add structural transition edges
builder.add_edge(START, "intent_parser")
builder.add_edge("intent_parser", "image_analyser")
builder.add_edge("image_analyser", "storyboard_writer")
builder.add_edge("storyboard_writer", "script_generator")
builder.add_edge("script_generator", "compiler_fixer")

# Route conditional transitions from the compiler_fixer node
builder.add_conditional_edges(
    "compiler_fixer",
    route_after_compile,
    {
        "render": "renderer",
        "retry": "increment_retry",
        "fail": "fail"
    }
)

builder.add_edge("increment_retry", "script_generator")
builder.add_edge("renderer", END)
builder.add_edge("fail", END)

def build_graph():
    """Compile and return the configured state graph."""
    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    mermaid_png = graph.get_graph().draw_mermaid()
    with open("outputs/graph_diagram.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid_png)
    print("Graph compiled successfully.")
