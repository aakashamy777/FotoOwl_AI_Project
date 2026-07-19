from typing import Literal
from langgraph.graph import StateGraph, START, END
from src.state import PipelineState

# Stub node functions (will be replaced by imports in a later step)
def intent_parser(state: PipelineState) -> dict:
    print("Executing node: intent_parser")
    return {}

def image_analyser(state: PipelineState) -> dict:
    print("Executing node: image_analyser")
    return {}

def storyboard_writer(state: PipelineState) -> dict:
    print("Executing node: storyboard_writer")
    return {}

def script_generator(state: PipelineState) -> dict:
    print("Executing node: script_generator")
    return {}

def compiler_fixer(state: PipelineState) -> dict:
    print("Executing node: compiler_fixer")
    return {}

def renderer(state: PipelineState) -> dict:
    print("Executing node: renderer")
    return {}

def fail_node(state: PipelineState) -> dict:
    print("Executing node: fail_node")
    return {"failure_reason": "Max compile retries reached without success."}

def increment_retry_node(state: PipelineState) -> dict:
    print("Executing node: increment_retry")
    return {"retry_count": state.get("retry_count", 0) + 1}

# Conditional routing logic
def route_after_compile(state: PipelineState) -> Literal["retry", "render", "fail"]:
    """Conditional router determining transition after the compiler_fixer.
    
    If compile_errors list is empty, we route to render.
    Otherwise, if we have not exceeded max_retries (default 3), we route to retry
    which increments the retry count and routes back to script_generator.
    If retry count exceeds max_retries, we route to the terminal fail node.
    """
    errors = state.get("compile_errors", [])
    if not errors:
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
