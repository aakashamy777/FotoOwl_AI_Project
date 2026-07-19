import os
import subprocess
from src.state import PipelineState

def renderer(state: PipelineState) -> PipelineState:
    """Render the generated Remotion composition to an MP4 video file using the Remotion CLI."""
    print("renderer: Starting video render...")
    output_path = "outputs/final_video.mp4"
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Ensure local image pathing works correctly inside the Remotion app at runtime
        src_data = "data"
        dest_data = "remotion-app/public/data"
        if os.path.exists(src_data) and not os.path.exists(dest_data):
            try:
                os.makedirs(os.path.dirname(dest_data), exist_ok=True)
                os.symlink(os.path.abspath(src_data), dest_data, target_is_directory=True)
                print("renderer: Symlinked data folder into remotion-app/public/")
            except Exception as e:
                print(f"renderer: Could not symlink, copying data folder instead: {e}")
                import shutil
                shutil.copytree(src_data, dest_data, dirs_exist_ok=True)
        
        # Build command: npx remotion render <entry-point> <composition-id> <output-path>
        cmd = [
            "npx", "remotion", "render",
            "remotion-app/src/index.ts",
            "EventReel",
            output_path
        ]
        
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if res.returncode == 0:
            print("renderer: Render completed successfully!")
            state["render_success"] = True
            state["final_output_path"] = os.path.abspath(output_path)
            state["failure_reason"] = None
        else:
            err_msg = res.stderr or res.stdout or "Unknown render error"
            print(f"renderer: Render failed: {err_msg}")
            state["render_success"] = False
            state["failure_reason"] = f"Remotion render exited with non-zero status: {err_msg}"
            
    except subprocess.TimeoutExpired:
        print("renderer: Render timed out.")
        state["render_success"] = False
        state["failure_reason"] = "Remotion render timed out."
    except Exception as e:
        print(f"renderer: Exception occurred: {e}")
        state["render_success"] = False
        state["failure_reason"] = f"Renderer exception: {str(e)}"
        
    return state
