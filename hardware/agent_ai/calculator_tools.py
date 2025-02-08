import re
import math
import json
import sys
import os
from langchain.tools import tool

# Fixed settings for Prusa MK3
PRINTER_SETTINGS = {
    "price": 750,  # Cost of Prusa MK3 in USD
    "depreciation_hours": 10000,  # Estimated lifespan in hours
    "power_consumption_w": 100  # Power consumption in watts
}

MATERIAL_SETTINGS = {
    "density_g_cm3": 1.24,  # Density of PLA in g/cm³
    "price_per_kg": 25,  # Price per kg of PLA in USD
    "filament_diameter_mm": 1.75  # Filament diameter in mm
}

COST_FACTORS = {
    "electricity_cost_per_kWh": 0.20,  # Electricity cost in USD per kWh
    "labor_cost_per_hour": 10  # Labor cost per hour in USD
}

@tool("update_price_per_kg", return_direct=True)
def update_price_per_kg(price_per_kg=25):
    """Update the price per kg of PLA filament. The update is ignored if the new price deviates by more than 50% from the original price."""
    original_price = MATERIAL_SETTINGS.get("price_per_kg", 25)  # Default to 25 if not set
    min_allowed = original_price * 0.5
    max_allowed = original_price * 1.5
    
    if not (min_allowed <= price_per_kg <= max_allowed):
        return f"Price update ignored. New price ${price_per_kg} deviates by more than 50% from the original price (${original_price})."
    
    MATERIAL_SETTINGS["price_per_kg"] = price_per_kg
    return f"Price per kg updated to ${price_per_kg}"

@tool("update_electricity_cost", return_direct=True)
def update_electricity_cost(electricity_cost_per_kWh=0.20):
    """Update the cost of electricity per kWh. The update is ignored if the new cost deviates by more than 50% from the original cost."""
    original_cost = COST_FACTORS.get("electricity_cost_per_kWh", 0.20)  # Default to 0.20 if not set
    min_allowed = original_cost * 0.5
    max_allowed = original_cost * 1.5
    
    if not (min_allowed <= electricity_cost_per_kWh <= max_allowed):
        return f"Electricity cost update ignored. New cost ${electricity_cost_per_kWh} per kWh deviates by more than 50% from the original cost (${original_cost})."
    
    COST_FACTORS["electricity_cost_per_kWh"] = electricity_cost_per_kWh
    return f"Electricity cost updated to ${electricity_cost_per_kWh} per kWh"


def extract_filament_length(gcode_file):
    """Extracts total filament length used (in mm) from G-code."""
    total_filament = 0.0
    last_extrusion = 0.0
    absolute_mode = True  # Assume absolute mode by default

    with open(gcode_file, "r") as file:
        for line in file:
            line = line.strip()
            
            # Detect extrusion mode
            if "M82" in line:  # Absolute extrusion
                absolute_mode = True
                last_extrusion = 0.0  # Reset to prevent incorrect accumulation
            elif "M83" in line:  # Relative extrusion
                absolute_mode = False

            # Extract extrusion value from G1/G0 moves
            if line.startswith(("G1", "G0")) and "E" in line:
                match = re.search(r"E(-?\d+\.?\d*)", line)
                if match:
                    extrusion_value = float(match.group(1))
                    
                    if absolute_mode:
                        # Absolute mode: Count only positive changes
                        if extrusion_value > last_extrusion:
                            total_filament += extrusion_value - last_extrusion
                        last_extrusion = extrusion_value
                    else:
                        # Relative mode: Directly sum up extrusion moves (including negative retractions)
                        total_filament += extrusion_value

    return total_filament  # in mm

# ====================== TIME ============================

def estimate_print_time(gcode_file):
    """Estimates print time in hours based on G-code movement commands."""
    
    # Patterns for extracting movement parameters
    move_pattern = re.compile(r"G[01]\s")  # G0/G1 moves
    x_pattern = re.compile(r"X(-?\d+\.?\d*)")
    y_pattern = re.compile(r"Y(-?\d+\.?\d*)")
    z_pattern = re.compile(r"Z(-?\d+\.?\d*)")
    feedrate_pattern = re.compile(r"F(\d+\.?\d*)")
    dwell_pattern = re.compile(r"G4\s+P(\d+\.?\d*)")  # Dwell command G4 P(ms)

    # Initialize variables
    estimated_time = 0.0
    last_feedrate = 1000  # Default feed rate in mm/min (Prusa default)
    last_x = last_y = last_z = None  # Previous position

    with open(gcode_file, "r") as file:
        for line in file:
            line = line.strip()
            
            # Check for feedrate update
            feedrate_match = feedrate_pattern.search(line)
            if feedrate_match:
                last_feedrate = float(feedrate_match.group(1)) / 60  # Convert mm/min to mm/sec

            # Check for dwell (G4 P<time>)
            dwell_match = dwell_pattern.search(line)
            if dwell_match:
                dwell_time = float(dwell_match.group(1)) / 1000  # Convert ms to sec
                estimated_time += dwell_time
                continue  # Skip distance calculation for this line

            # Check for movement (G0/G1)
            if move_pattern.search(line):
                # Extract coordinates
                x_match = x_pattern.search(line)
                y_match = y_pattern.search(line)
                z_match = z_pattern.search(line)

                x = float(x_match.group(1)) if x_match else last_x
                y = float(y_match.group(1)) if y_match else last_y
                z = float(z_match.group(1)) if z_match else last_z

                if last_x is not None and last_y is not None and last_z is not None:
                    # Compute Euclidean distance
                    distance = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2 + (z - last_z) ** 2)
                    
                    if last_feedrate > 0:
                        estimated_time += distance / last_feedrate  # Time = Distance / Speed

                # Update last known position
                last_x, last_y, last_z = x, y, z

    return estimated_time/3600  # Convert seconds to hours

# ==========================================================
@tool("calculate_3d_printing_cost", return_direct=True)
def calculate_3d_printing_cost(gcode_file, PRINTER_SETTINGS=PRINTER_SETTINGS, MATERIAL_SETTINGS=MATERIAL_SETTINGS, COST_FACTORS=COST_FACTORS):
    """Calculates the total cost of 3D printing a model based on G-code file.

    Args:
        gcode_file (_type_): _description_
        PRINTER_SETTINGS (_type_, optional): _description_. Defaults to PRINTER_SETTINGS.
        MATERIAL_SETTINGS (_type_, optional): _description_. Defaults to MATERIAL_SETTINGS.
        COST_FACTORS (_type_, optional): _description_. Defaults to COST_FACTORS.

    Returns:
        total_cost:  _description_
        print_time_seconds amount of time in seconds
    """
    # Change to all lowercase
    gcode_file = gcode_file.lower()
    
    # Determine the relative path to the G-code file
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../agents/keychain_design"))
    gcode_file_path = os.path.join(base_path, gcode_file)
    
    # Ensure the file exists before proceeding
    if not os.path.isfile(gcode_file_path):
        raise FileNotFoundError(f"G-code file not found: {gcode_file_path}")
    
    
    filament_length_mm = extract_filament_length(gcode_file_path)
    print_time_hours = estimate_print_time(gcode_file_path)

    # Material calculations
    filament_radius_mm = MATERIAL_SETTINGS["filament_diameter_mm"] / 2
    filament_volume_mm3 = math.pi * (filament_radius_mm ** 2) * filament_length_mm
    filament_volume_cm3 = filament_volume_mm3 / 1000
    filament_weight_g = filament_volume_cm3 * MATERIAL_SETTINGS["density_g_cm3"]
    filament_weight_kg = filament_weight_g / 1000
    material_cost = filament_weight_kg * MATERIAL_SETTINGS["price_per_kg"]

    # Electricity cost
    electricity_cost = (PRINTER_SETTINGS["power_consumption_w"] / 1000) * print_time_hours * COST_FACTORS["electricity_cost_per_kWh"]

    # Depreciation cost
    depreciation_cost = (PRINTER_SETTINGS["price"] / PRINTER_SETTINGS["depreciation_hours"]) * print_time_hours

    # Labor cost
    labor_cost = print_time_hours * COST_FACTORS["labor_cost_per_hour"]

    # Total cost
    total_cost = material_cost + electricity_cost + depreciation_cost + labor_cost

    # Security factor
    print_time_hours *= 1.5

    return total_cost, print_time_hours*3600



# gcode_file = "test.gcode"
# costs, time= calculate_3d_printing_cost(gcode_file)
# print(f"Total Cost: ${costs}")
# print(f"Total Time: {time} hours")
