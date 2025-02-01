import os
import numpy as np
import cv2 as cv
import trimesh as tm
from PIL import Image, ImageFilter

# Load the silhouette image (for extrusion)
input_image_path = "input_image.png"  # Replace with your image file
output_stl_path = "output_file.stl"

# Open and preprocess image
img = Image.open(input_image_path).convert("L")
img = img.filter(ImageFilter.GaussianBlur(radius=1))
threshold = 128
img = img.point(lambda p: 255 if p > threshold else 0)
img = img.resize((100, 100))
pixels = np.array(img)

# Define heights
base_height = 0  # Circular base height
ant_height = 4  # Raised ant shape height (above base)

# Convert image to heightmap (1 for background, raised for ant)
height_map = np.where(pixels < threshold, ant_height, base_height).astype(np.float32)

# Function to create a 3D mesh from the heightmap with trimmed background and a separate loop for a keychain hole
def create_mesh_from_heightmap(heightmap, z_scale=5):
    """Creates a 3D mesh from a heightmap and embeds it onto a circular base, trimming excess background and adding a separate loop with a keychain hole."""
    
    heightmap = cv.resize(heightmap, (128, 128), interpolation=cv.INTER_CUBIC)
    
    # Define circular base parameters
    center_x, center_y = 64, 64  # Center of the circular base
    base_radius = 75  # Define radius of the circular base
    hole_radius = 5  # Define radius of the keychain hole
    loop_radius = 15  # Radius of the additional loop for the keychain
    loop_position = (center_x - base_radius - loop_radius + 5, center_y)  # Position to the left
    
    # Create vertices and faces for ant extrusion, but only within the circular base
    vertices = []
    faces = []
    
    for x in range(heightmap.shape[0] - 1):
        for y in range(heightmap.shape[1] - 1):
            distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= base_radius-5:
                v1 = (x, y, heightmap[x, y] * z_scale)
                v2 = (x+1, y, heightmap[x+1, y] * z_scale)
                v3 = (x, y+1, heightmap[x, y+1] * z_scale)
                v4 = (x+1, y+1, heightmap[x+1, y+1] * z_scale)
                vertices.extend([v1, v2, v3, v4])
                faces.append([len(vertices)-4, len(vertices)-3, len(vertices)-2])
                faces.append([len(vertices)-2, len(vertices)-3, len(vertices)-1])
    
    ant_mesh = tm.Trimesh(vertices=vertices, faces=faces)

    # Create a circular base (trimmed background)
    base = tm.creation.cylinder(radius=base_radius, height=3, sections=100)
    base.apply_scale([1.0, 1.2, 1.0])
    base.apply_translation([center_x, center_y, -1])
    
    """ # Create a separate loop for the keychain
    loop = tm.creation.cylinder(radius=loop_radius, height=3, sections=100)
    loop.apply_translation([loop_position[0], loop_position[1], -1])
    
    # Create a keychain hole inside the loop
    hole = tm.creation.cylinder(radius=hole_radius, height=3 + 1, sections=50)
    hole.apply_translation([loop_position[0], loop_position[1], -1])
    
    # Subtract the hole from the loop
    loop = loop.difference(hole) """
    
    # Create a keychain hole
    hole_position = (center_x, center_y - 80)  # Position near the edge
    hole = tm.creation.cylinder(radius=hole_radius, height=3+1, sections=50)
    hole.apply_translation([hole_position[0], hole_position[1], -1])
    
    # Subtract the hole from the base
    base = base.difference(hole)
    
    # Combine the base and trimmed ant extrusion
    final_mesh = tm.util.concatenate([base, ant_mesh])

    
    # Combine the base, loop, and trimmed ant extrusion
    #final_mesh = tm.util.concatenate([base, loop, ant_mesh])
    
    return final_mesh

# Generate STL mesh with trimmed background and keychain loop
final_mesh = create_mesh_from_heightmap(height_map, z_scale=1)
final_mesh.export(output_stl_path)

print(f"✅ STL file saved as {output_stl_path}")

