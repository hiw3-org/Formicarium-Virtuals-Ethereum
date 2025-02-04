import numpy as np
import cv2 as cv
import trimesh as tm
from PIL import Image, ImageFilter

def image_to_stl(input_image_path, output_stl_path, base_height=5, ant_height=10, z_scale=1):
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
    height_map = np.where(pixels < threshold, ant_height, base_height).astype(np.float32)
    
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
                    v2 = (x+1, y, heightmap[x+1, y] * z_scale)
                    v3 = (x, y+1, heightmap[x, y+1] * z_scale)
                    v4 = (x+1, y+1, heightmap[x+1, y+1] * z_scale)
                    vertices.extend([v1, v2, v3, v4])
                    faces.append([len(vertices)-4, len(vertices)-3, len(vertices)-2])
                    faces.append([len(vertices)-2, len(vertices)-3, len(vertices)-1])
        
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
    final_mesh.export(output_stl_path)
    print(f"✅ STL file saved as {output_stl_path}")
