import base64
import os
import subprocess
from pathlib import Path
from hardware.agent_ai import config
from pydantic import BaseModel


# Pydantic model to validate incoming request data
class STLRequest(BaseModel):
    stl_file: str  # Base64-encoded STL file
    box_size: list  # Bounding box dimensions
    stl_name: str  # STL file name

def slice_stl(input_stl_path: str, box_size=[100, 100, 100]) -> str:
    """Slice an STL file using PrusaSlicer and save the output G-code file."""
    output_gcode_path = input_stl_path.with_suffix(".gcode")
    
    input_stl_path = os.path.abspath(input_stl_path)
    output_gcode_path = os.path.abspath(output_gcode_path)
    
    # Run PrusaSlicer in the command line
    command = (
        f"{config.prusa_slicer_path} {config.prusa_settings}"
        f" --scale-to-fit {box_size[0]},{box_size[1]},{box_size[2]} "
        f"--output {output_gcode_path} {input_stl_path} "
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f"PrusaSlicer failed with error code {process.returncode}: {stderr.decode()}")

    return output_gcode_path

def handle_stl_request(stl_file: str, stl_name: str, box_size: list) -> str:
    """Handle the decoding and saving of STL file, then generate the G-code."""
    try:
        # Decode the STL file
        stl_data = base64.b64decode(stl_file)
        
        # Directory to store the STL and G-code
        gcode_dir = Path("hardware/gcode")
        gcode_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the STL file temporarily
        stl_path = gcode_dir / f"{stl_name}.stl"
        with open(stl_path, "wb") as stl_file:
            stl_file.write(stl_data)
        
        # Generate G-code
        gcode_path = slice_stl(stl_path, box_size)
        
        return str(gcode_path)
    
    except Exception as e:
        raise Exception(f"Error processing STL file: {str(e)}")
