import trimesh
from trimesh.scene import Scene
from PIL import Image, ImageEnhance
import io
import sys
import numpy as np

def convert_stl_to_image(stl_path, output_path, rotation=(0, 0, 0), contrast_factor=1.8, brightness_factor=1.1):
    try:
        # Load the STL mesh
        mesh = trimesh.load_mesh(stl_path)

        # Ensure all faces have the same color (for better contrast)
        if hasattr(mesh.visual, "vertex_colors"):
            mesh.visual.vertex_colors = [200, 200, 200, 255]  # Light gray color

        # Center the model before rotating
        mesh.apply_translation(-mesh.centroid)

        # Apply rotation (convert degrees to radians)
        rx, ry, rz = np.radians(rotation)
        rotation_matrix = trimesh.transformations.euler_matrix(rx, ry, rz)

        # Transform the mesh
        mesh.apply_transform(rotation_matrix)

        # Create a scene for rendering
        scene = Scene([mesh])

        # Adjust camera to ensure full model visibility
        bounding_box = mesh.bounding_box.extents
        camera_distance = max(bounding_box)  # Move camera further
        scene.camera_transform = trimesh.transformations.translation_matrix([0, 0, camera_distance])

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

        # Save the improved image
        image.save(output_path)
        print(f"Image saved successfully at: {output_path}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    stl_file = "examples_stl/output_file.stl"
    output_file = "output_image.png"

    # Default rotation (no rotation)
    rotation_angles = (0, -60, -90)


    convert_stl_to_image(stl_file, output_file, rotation=rotation_angles)
