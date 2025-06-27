import subprocess
import numpy as np
import matplotlib.pyplot as plt
import json
import pathlib

src_path = pathlib.Path(__file__).parent.resolve()
alma_path = pathlib.Path(__file__).parent.parent.resolve() / "ALMA3/"
default_config_file = "config.ALMApy_config.dat"
default_model_file = "ALMApy_model.dat"
default_data_file = "ALMApy_k_data.dat"
default_parameter_file = "parameters.json"

def change_param(param_name, param_value, config_file=default_config_file, parameter_file=default_parameter_file):
    # Open parameters file to get the strings to look for in the config file
    with open(src_path/parameter_file, "r") as f:
        params = json.load(f)
    
    # Open the config file and read it
    with open(src_path/config_file, 'r') as f:
        lines = f.readlines()
    
    # Search for the parameter and change its value
    for i, line in enumerate(lines):
        if params[param_name] in line:
            lines[i] = " " + str(param_value) + " "*max(5,30-len(str(param_value))) + "! " + params[param_name] + "\n"
    
    # Save the changed lines to the config file
    with open(src_path/config_file, 'w') as f:
        f.writelines(lines)

def change_model_file(radii, densities, rigidities, viscosities, model_types, model_file=default_model_file):
    """
    Writes a model file for ALMA using provided layer properties.

    Parameters:
        output_path (str or Path): Destination file path.
        radii (list of float): Radii in meters.
        densities (list of float): Densities in kg/m^3.
        rigidities (list of float): Rigidity in Pascals.
        viscosities (list of float): Viscosity in Pa.s.
        model_types (list of str): Rheology type per layer (e.g., 'maxwell', 'newton').
    """


    # There must be at least two layers in the model
    if len(radii) == 1:
        radii = [radii[0]/2,radii[0]]
        densities = densities*2
        rigidities = rigidities*2
        viscosities = viscosities*2
        model_types = model_types*2

    # Create the file
    with open(src_path/model_file, "w") as f:
        f.write("!------------------------------------------------------------\n")
        f.write("! radius,    density,      rigidity     viscosity\n")
        f.write("!  (m)       (kg/m^3)        (Pa)         (Pa.s) \n")
        f.write("!------------------------------------------------------------\n")

        for radius, density, rigidity, viscosity, model_type in zip(radii, densities, rigidities, viscosities, model_types):
            f.write(f"{radius:<12.5g} {density:<10.5g} {rigidity:<12.5g} {viscosity:<12.5g} {model_type}\n")

def execute_alma(show_output=False, show_start_stop=True, config_file=default_config_file, model_file=default_model_file, parameter_file=default_parameter_file):
    change_param("model_file_path", src_path/model_file, config_file, parameter_file)
    change_param("output_file_h", src_path/"ALMApy_h_data.dat", config_file, parameter_file)
    change_param("output_file_k", src_path/"ALMApy_k_data.dat", config_file, parameter_file)
    change_param("output_file_l", src_path/"ALMApy_l_data.dat", config_file, parameter_file)
    if show_start_stop:
        print("Running ALMA3...")
    try:
        result = subprocess.run([alma_path/"alma.exe", src_path/config_file], check=True, capture_output=True, text=True, cwd=alma_path)

        # Output the stdout and stderr
        if show_output:
            print("Output:\n", result.stdout)
            print("Errors (if any):\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print("There was an error running the command:")
        print(e.stderr)
    if show_start_stop:
        print("Done running!")

def read_output(data_file=default_data_file, complex=False):
    periods = []
    k_love_numbers = []
    k2_imaginary = []

    # Read file
    with open(src_path/data_file, 'r') as file:
        for line in file:
            # Skip comments and empty lines
            if line.strip().startswith("#") or not line.strip():
                continue
            # Split and parse values
            values = line.split()
            if not complex:
                if len(values) == 2:
                    period = float(values[0])
                    k_val = float(values[1])
                    periods.append(period)
                    k_love_numbers.append(k_val)
            else:
                if len(values) == 3:
                    period = float(values[0])
                    k_val = float(values[1])
                    k2_imaginary_val = float(values[2])
                    periods.append(period)
                    k_love_numbers.append(k_val)
                    k2_imaginary.append(k2_imaginary_val)
    if not complex:
        return periods, k_love_numbers
    return periods, k_love_numbers, k2_imaginary

def run_alma(radii, densities, rigidities, viscosities, model_types, show_output=False, show_start_stop=True):

    # All inputs must have the same length
    no_layers = None

    # Convert to numpy arrays
    if isinstance(radii, float) or isinstance(radii, int):
        radii = [radii, radii/2]
        densities = [densities]*2
        rigidities = [rigidities]*2
        viscosities = [viscosities]*2
        model_types = [model_types]*2
    
    # Check if all inputs have the same size
    if not (len(radii) == len(densities) == len(rigidities) == len(viscosities) == len(model_types)):
        raise ValueError("All input lists must be of the same length.")
    else:
        no_layers = len(radii)

    # Set the correct number of layers in the config file
    change_param("no_layers", no_layers, config_file=default_config_file, parameter_file=default_parameter_file)

    # Create the model file
    change_model_file(radii, densities, rigidities, viscosities, model_types, model_file=default_model_file)

    # Run alma
    execute_alma(show_output=show_output, show_start_stop=show_start_stop, config_file=default_config_file)

    # Read output
    t, k = read_output()

    return t,k

def get_k2_vs_radius(core_radius, atmosphere_radii, densities, rigidities, viscosities):
    k2 = np.zeros(len(atmosphere_radii))
    for i in range(len(atmosphere_radii)):
        _,k = run_alma(radii = [atmosphere_radii[i], core_radius],
                    densities = densities,
                    rigidities = rigidities,
                    viscosities = viscosities,
                    model_types = ["newton", "maxwell"],
                    show_start_stop = False)
        k2[i] = k[0]

    return k2