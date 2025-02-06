import re
import math

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

    return estimated_time / 3600  # Convert seconds to hours

# ==========================================================

def calculate_3d_printing_cost(gcode_file, PRINTER_SETTINGS=PRINTER_SETTINGS, MATERIAL_SETTINGS=MATERIAL_SETTINGS, COST_FACTORS=COST_FACTORS):
    """Calculates the cost of 3D printing using fixed Prusa MK3 settings."""
    filament_length_mm = extract_filament_length(gcode_file)
    print_time_hours = estimate_print_time(gcode_file)

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

    return total_cost, print_time_hours



gcode_file = "test.gcode"
costs, time= calculate_3d_printing_cost(gcode_file)
print(f"Total Cost: ${costs}")
print(f"Total Time: {time} hours")