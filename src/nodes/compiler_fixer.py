import os
import subprocess
from src.state import PipelineState, CompileError

def compiler_fixer(state: PipelineState) -> PipelineState:
    """Validate the Remotion script by writing it to EventReel.tsx and running compile check."""
    script = state.get("remotion_script")
    if "compile_errors" not in state or state["compile_errors"] is None:
        state["compile_errors"] = []

    if not script:
        print("compiler_fixer: No remotion_script found.")
        state["compile_errors"].append(
            CompileError(error_message="Missing remotion_script in state.", error_type="compile_error")
        )
        return state

    # Ensure target directory exists and write the code
    reel_path = "remotion-app/src/EventReel.tsx"
    try:
        os.makedirs(os.path.dirname(reel_path), exist_ok=True)
        with open(reel_path, "w", encoding="utf-8") as f:
            f.write(script)

        # Run bundle check to verify syntax and typescript correctness
        cmd = ["npx", "remotion", "bundle", "src/index.ts"]
        res = subprocess.run(
            cmd,
            cwd="remotion-app",
            capture_output=True,
            text=True,
            timeout=30
        )

        if res.returncode != 0:
            err_msg = res.stderr or res.stdout or "Unknown compilation error"
            print(f"compiler_fixer: Compile failed with error:\n{err_msg}")
            state["compile_errors"].append(
                CompileError(error_message=err_msg, error_type="compile_error")
            )
            state["render_success"] = False
        else:
            print("compiler_fixer: Compile check succeeded!")
            # Temporary flag indicating compilation was clean
            state["render_success"] = True

    except subprocess.TimeoutExpired:
        print("compiler_fixer: Compile check timed out.")
        state["compile_errors"].append(
            CompileError(error_message="Compilation check timed out.", error_type="compile_error")
        )
        state["render_success"] = False
    except Exception as e:
        print(f"compiler_fixer: Exception occurred: {e}")
        state["compile_errors"].append(
            CompileError(error_message=str(e), error_type="compile_error")
        )
        state["render_success"] = False

    return state
