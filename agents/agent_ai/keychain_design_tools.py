import requests
from pathlib import Path
from langchain.tools import tool
import openai
import trimesh as tm
from PIL import Image, ImageFilter
import numpy as np
import cv2 as cv
import hashlib
import os
import sys
import subprocess
from PIL import Image, ImageEnhance
from trimesh.scene import Scene
import io
import secrets

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import agents.agent_ai.config as config

output_folder = Path("agents/keychain_design")

def shorten_filename(prompt: str) -> str:
    hash_digest = hashlib.md5(prompt.encode()).hexdigest()[:8]  # Get the first 8 characters of the hash
    return f"{hash_digest}.png"

def generate_random_id(prompt: str) -> str:
    # Use the prompt to seed the randomness (or you can ignore the prompt if you want totally random)
    random_seed = secrets.token_hex(20)  # Generates 40 characters of hex (20 bytes)
    
    # This generates a random "Ethereum-like" address, 40 characters (hex) with '0x' prefix
    eth_address = '0x' + random_seed[:40].lower()
    
    shortened_address = eth_address[2:]  # Skip '0x' prefix 

    return f"{shortened_address}.png"


def image_to_stl(
    input_image_path, output_stl_path, base_height=15, ant_height=30, z_scale=1, max_dimensions=(200, 200, 250)
):
    """
    Converts an input image into a 3D STL file with an extruded base and a keychain hole.

    Parameters:
    - input_image_path: str, path to the input image
    - output_stl_path: str, path to save the STL file
    - base_height: int, height of the circular base
    - ant_height: int, height of the extruded object
    - z_scale: int, scaling factor for the extrusion
    """
    # Load and preprocess image
    img = Image.open(input_image_path).convert("L")
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    threshold = 128
    img = img.point(lambda p: 255 if p > threshold else 0)
    img = img.resize((512, 512))
    pixels = np.array(img)

    # Convert image to heightmap
    height_map = np.where(pixels < threshold, ant_height, 0).astype(np.float32)

    def create_mesh_from_heightmap(heightmap):
        """Creates a 3D mesh from a heightmap and embeds it onto a circular base, adding a keychain hole."""
        heightmap = cv.resize(heightmap, (512, 512), interpolation=cv.INTER_LANCZOS4)

        # Define circular base parameters
        center_x, center_y = 256, 256  # Center of the circular base
        base_radius = 300  # Define radius of the circular base
        hole_radius = 20  # Define radius of the keychain hole

        # Create vertices and faces for the extruded object within the circular base
        vertices = []
        faces = []

        for x in range(heightmap.shape[0] - 1):
            for y in range(heightmap.shape[1] - 1):
                distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance <= base_radius - 5:
                    v1 = (x, y, heightmap[x, y] * z_scale)
                    v2 = (x + 1, y, heightmap[x + 1, y] * z_scale)
                    v3 = (x, y + 1, heightmap[x, y + 1] * z_scale)
                    v4 = (x + 1, y + 1, heightmap[x + 1, y + 1] * z_scale)
                    vertices.extend([v1, v2, v3, v4])
                    faces.append([len(vertices) - 4, len(vertices) - 3, len(vertices) - 2])
                    faces.append([len(vertices) - 2, len(vertices) - 3, len(vertices) - 1])

        ant_mesh = tm.Trimesh(vertices=vertices, faces=faces)
        ant_mesh = ant_mesh.subdivide(2)

        # Create a circular base
        base = tm.creation.cylinder(radius=base_radius, height=base_height, sections=200)
        base.apply_scale([1.0, 1.2, 1.0])
        base.apply_translation([center_x, center_y, -1])

        # Create a keychain hole
        hole_position = (center_x, center_y - 280)
        hole = tm.creation.cylinder(radius=hole_radius, height=base_height + 1, sections=200)
        hole.apply_translation([hole_position[0], hole_position[1], -1])

        # Subtract the hole from the base
        base = base.difference(hole)

        # Combine the base and extruded object
        final_mesh = tm.util.concatenate([base, ant_mesh])

        return final_mesh

    # Generate STL mesh and save file
    final_mesh = create_mesh_from_heightmap(height_map)

    # # **Scale down the STL to fit within max 3D printer dimensions**
    # current_size = final_mesh.extents  # Get the size of the mesh (width, depth, height)
    # scale_factors = [max_dim / cur_dim for max_dim, cur_dim in zip(max_dimensions, current_size)]
    # scale_factor = min(scale_factors)  # Use the smallest factor to keep proportions

    # final_mesh.apply_scale(scale_factor)  # Apply uniform scaling

    final_mesh.export(output_stl_path)

def generate_image(prompt: str) -> str:
    """Generate an image using DALL·E and return the image URL."""
    response = openai.images.generate(
        model=config.dalle_model,
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url",
    )
    # Access the URL using attribute access
    return response.data[0].url

def slice_stl(input_stl_path: str, box_size=[100,100,100]) ->  str:
    """Slice an STL file using PrusaSlicer and save the output G-code file."""
    output_gcode_path = input_stl_path.with_suffix(".gcode")
    
    input_stl_path = os.path.abspath(input_stl_path)
    output_gcode_path = os.path.abspath(output_gcode_path)
    
    # Run PrusaSlicer in the command line
    command = (
        f"{config.prusa_slicer_path} {config.prusa_settings}"
        f"--scale-to-fit {box_size[0]},{box_size[1]},{box_size[2]} "
        f"--output {output_gcode_path} {input_stl_path} "
    )
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f"PrusaSlicer failed with error code {process.returncode}: {stderr.decode()}")

    return output_gcode_path

@tool
def generate_image_tool(prompt: str) -> str:
    """Generate a grayscale image based on the user's prompt and save it locally."""
    # Ensure the image is grayscale
    grayscale_prompt = f"{prompt} in grayscale"
    image_url = generate_image(grayscale_prompt)

    # Download the image
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image: {response.status_code}")
    
    # Save the image to a folder
    output_folder.mkdir(exist_ok=True)  # Create the folder if it doesn't exist

    # Sanitize the prompt to create a valid filename
    sanitized_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()
    image_path = output_folder / generate_random_id(sanitized_prompt)

    with open(image_path, "wb") as f:
        f.write(response.content)
        
    return str(image_path)  # Return the image path as a string


@tool
def generate_keychain_stl_tool(image_path: str) -> str:
    """Generate a stlfile image based on the user's image and save it locally."""    
    output_stl_path = output_folder / f"{Path(image_path).stem}.stl"
    output_stl_path.parent.mkdir(exist_ok=True)
    
    image_path = output_folder / f"{Path(image_path)}"
    

    image_to_stl(image_path, str(output_stl_path))

    return str(image_path)  # Return the image path as a string

@tool
def generate_keychain_gcode_tool(stl_path: str, box_size=[100,100,100]) -> str:
    """Generate a gcode file based on the user's stl file and save it locally."""
    stl_path = output_folder / f"{Path(stl_path).stem}.stl"
    stl_path.parent.mkdir(exist_ok=True)
    
    output_gcode = slice_stl(stl_path, box_size)

    return str(output_gcode)

@tool
def get_offer_from_printer_agent(gcode_path: str) -> str:
    """Get the price and time estimate for the 3D print from an external API."""
    
    url = "http://localhost:8080/api/create_order_request"
    payload = {
        "prompt": f"Please calculate the price and print time for {gcode_path}"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get("response", "No response content found.")
    else:
        return f"Error: {response.status_code}, {response.text}"
    
    
def convert_stl_to_image(stl_path, rotation=(0, -60, -90), contrast_factor=1.8, brightness_factor=1.1):
    try:
        stl_path = output_folder / f"{Path(stl_path).stem}.stl"
        stl_path.parent.mkdir(exist_ok=True)
        # Load the STL mesh
        mesh = tm.load_mesh(stl_path)

        # Ensure all faces have the same color (for better contrast)
        if hasattr(mesh.visual, "vertex_colors"):
            mesh.visual.vertex_colors = [200, 200, 200, 255]  # Light gray color

        # Center the model before rotating
        mesh.apply_translation(-mesh.centroid)

        # Apply rotation (convert degrees to radians)
        rx, ry, rz = np.radians(rotation)
        rotation_matrix = tm.transformations.euler_matrix(rx, ry, rz)

        # Transform the mesh
        mesh.apply_transform(rotation_matrix)

        # Create a scene for rendering
        scene = Scene([mesh])

        # Adjust camera to ensure full model visibility
        bounding_box = mesh.bounding_box.extents
        camera_distance = max(bounding_box)  # Move camera further
        scene.camera_transform = tm.transformations.translation_matrix([0, 0, camera_distance])

        # Debug: Show the scene before rendering
        # scene.show()  # Uncomment to preview before saving

        # Render the scene to an image buffer
        image_bytes = scene.save_image(resolution=[640, 480])
        if image_bytes is None:
            raise ValueError("Failed to render image from STL.")

        # Convert bytes to a PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        # Apply brightness and contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast_factor)  # Increase contrast

        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness_factor)  # Increase brightness
        
        output_path = output_folder / f"{Path(stl_path).stem}_stl.png"

        # Save the improved image
        image.save(output_path)
        return str(output_path)

    except Exception as e:
        print(f"Error: {e}")

# main function, call image_to_stl
if __name__ == "__main__":
    id = generate_random_id("sfsdf")
    print(id)
    
    
