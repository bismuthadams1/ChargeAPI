import subprocess
import tempfile
from multiprocessing import Process
import json
from typing import Optional
import numpy as np
import os
import logging
import ChargeAPI

def handle_esp_request(charge_model: str, 
                       conformer_mol: str, 
                       batched: bool = False, 
                       broken_up: bool = False,
                       grid: Optional[np.ndarray] = None) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model. Batched option accepts a JSON of molecule names and their
    corresponding forms in molblocks. 
    """
    if batched:
        batched_option = '--batched'
    else:
        batched_option = '--not_batched'

    if broken_up:
        broken_up_option = '--broken_up'
        batched_option = '--not_batched'
    else:
        broken_up_option = '--not_broken_up'

    if grid is not None:
        grid_str = np.array2string(grid.flatten())  # Convert the grid array to a string to pass via the command line
        grid_command = f"--grid_array '{grid_str}'"
    else:
        grid_command = ''
        
    if charge_model == 'RIN':
            script_path = f'{os.path.dirname(ChargeAPI.__file__)}/esp_models/riniker_model.py'
            cmd = (
                f"conda run -n riniker python {script_path} \
                --conformer '{conformer_mol}' \
                {batched_option}  \
                {broken_up_option} \
                {grid_command}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return prepare_json_outs(charge_result, batched=batched, broken_up=broken_up)
    else:
            raise NameError

def prepare_json_outs(charge_result: subprocess.CompletedProcess, batched: bool = False, broken_up: bool = False) -> json:
    """
    grabs data from subprocess and produces a json of the output
    Paramters
    --------
    charge_result:  subprocess.CompletedProcess
        Result of the subprocess run command in/out/error info
    """

    complete_result_list = charge_result.stdout.decode()  # Convert the output to a list if it's a string
    print(complete_result_list)

    if not batched:
        if not broken_up:
            (esp, grid) = complete_result_list.split('OO')
            # Create JSON response
            json_response = {
                'esp_result': esp.strip('\n\n'),
                'grid':grid.strip('\n\n'),
                'error': charge_result.stderr.decode()  # Include the error message if any
            }
        else:             
            (monopole, dipole, quadropole) = complete_result_list.split('OO')
            # Create JSON response
            json_response = {
                'monopole': monopole.strip('\n\n'),
                'dipole':dipole.strip('\n\n'),
                'quadropole':quadropole.strip('\n\n'),
                'error': charge_result.stderr.decode()  # Include the error message if any
            }
    else:
        path_to_result = complete_result_list
        # Create JSON response
        json_response = {
            'file_path': path_to_result.strip('\n\n'),
            'error': charge_result.stderr.decode()  # Include the error message if any
        }
    logging.info(json_response)
    # Return the charge result as a list and the JSON response        
    return json_response


def main():
    mol = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    json_result = handle_esp_request(charge_model = 'RIN', 
                                        conformer_mol = mol,
                                        batched=False)
    print(json_result)

if __name__ == '__main__':
    main()
