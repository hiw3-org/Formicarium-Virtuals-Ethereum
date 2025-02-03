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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def generate_image(prompt: str) -> str:
    """Generate an image using DALL·E and return the image URL."""
    response = openai.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="512x512",
        response_format="url",
    )
    # Access the URL using attribute access
    return response.data[0].url


def shorten_filename(prompt: str) -> str:
    hash_digest = hashlib.md5(prompt.encode()).hexdigest()[:8]  # Get the first 8 characters of the hash
    return f"{hash_digest}.png"


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

    # **Scale down the STL to fit within max 3D printer dimensions**
    current_size = final_mesh.extents  # Get the size of the mesh (width, depth, height)
    scale_factors = [max_dim / cur_dim for max_dim, cur_dim in zip(max_dimensions, current_size)]
    scale_factor = min(scale_factors)  # Use the smallest factor to keep proportions

    final_mesh.apply_scale(scale_factor)  # Apply uniform scaling

    final_mesh.export(output_stl_path)
    print(f"✅ STL file saved as {output_stl_path}")


@tool
def generate_keychain_tool(prompt: str) -> str:
    """Generate a grayscale image based on the user's prompt and save it locally."""
    # Ensure the image is grayscale
    grayscale_prompt = f"{prompt} in grayscale"
    image_url = generate_image(grayscale_prompt)

    # Download the image
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image: {response.status_code}")

    # Save the image to a folder
    output_folder = Path("agents/keychain_design")
    output_folder.mkdir(exist_ok=True)  # Create the folder if it doesn't exist

    # Sanitize the prompt to create a valid filename
    sanitized_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).rstrip()
    image_path = Path("agents/keychain_design") / shorten_filename(sanitized_prompt)

    with open(image_path, "wb") as f:
        f.write(response.content)

    output_stl_path = Path("agents/keychain_design") / f"{Path(image_path).stem}.stl"
    output_stl_path.parent.mkdir(exist_ok=True)

    image_to_stl(image_path, str(output_stl_path))

    return str(image_path)  # Return the image path as a string


# main function, call image_to_stl
if __name__ == "__main__":
    input_image_path = "agents/keychain-design/564ebab1.png"
    output_stl_path = "agents/keychain-design/564ebab1.stl"
    image_to_stl(input_image_path, output_stl_path)
