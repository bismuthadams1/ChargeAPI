import subprocess
import json
import numpy as np
from typing import Optional, Dict, Any
import os
import logging
import tempfile
import ChargeAPI

# Define available ESP models and their conda environments/model paths.
model_locations = {
    'RIN': ['riniker', '/esp_models/riniker_model.py']
}

def _esp_requester(
    charge_model: str,
    batched: str,
    broken_up: str,
    conformer_mol: str,
    grid: Optional[np.ndarray],
    batched_grid: str,
    protein: bool
) -> Dict[str, Any]:
    """
    Internal function to build and execute the ESP charge request.

    Parameters
    ----------
    charge_model : str
        The ESP charge model to use.
    batched : str
        Option for batched mode ('--batched' or '--not_batched').
    broken_up : str
        Option for broken-up mode ('--broken_up' or '--not_broken_up').
    conformer_mol : str
        The molecule conformer string.
    grid : Optional[np.ndarray]
        Optional grid array.
    batched_grid : str
        Option for batched grid ('--batched_grid' or '--not_batched_grid').
    protein : bool
        Whether the molecule is a protein.

    Returns
    -------
    Dict[str, Any]
        A JSON-style dictionary containing the result and any errors.
    """
    try:
        env, model_path = model_locations[charge_model]
    except KeyError as e:
        raise Exception("ESP charge model does not exist") from e

    script_path = f'{os.path.dirname(ChargeAPI.__file__)}'+ model_path

    tmp_file_path = None
    if protein:
        # Write conformer data to a temporary file in protein mode.
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdb') as tmp_file:
            tmp_file.write(conformer_mol)
            input_path = tmp_file.name
        protein_option = '--protein'
        tmp_file_path = input_path
    else:
        input_path = conformer_mol
        protein_option = '--not_protein'

    # Build the command list.
    cmd = [
        "conda", "run", "--no-capture-output", "-n", env, "python", script_path,
        "--conformer", input_path,
        batched,
        broken_up,
        protein_option
    ]

    if grid is not None:
        np.set_printoptions(threshold=np.inf)
        grid_str = np.array2string(grid.flatten(), separator=' ', precision=8)
        cmd.extend(["--grid_array", grid_str])

    cmd.append(batched_grid)

    logging.info("Executing command: %s", " ".join(cmd))
    charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Clean up temporary file if created.
    if tmp_file_path is not None:
        os.remove(tmp_file_path)

    return prepare_json_outs(charge_result, batched == '--batched', broken_up == '--broken_up')

def handle_esp_request(
    charge_model: str,
    conformer_mol: str,
    batched: bool = False,
    broken_up: bool = False,
    grid: Optional[np.ndarray] = None,
    batched_grid: bool = False,
    protein: bool = False
) -> Dict[str, Any]:
    """
    Handle the ESP charge request and run the specified charge model.

    Parameters
    ----------
    charge_model : str
        The ESP charge model to use.
    conformer_mol : str
        The molecule conformer string.
    batched : bool, optional
        Whether to use batched mode, by default False.
    broken_up : bool, optional
        Whether to use broken-up mode, by default False.
    grid : Optional[np.ndarray], optional
        Optional grid array.
    batched_grid : bool, optional
        Whether to use batched grid, by default False.
    protein : bool, optional
        Whether the molecule is a protein, by default False.

    Returns
    -------
    Dict[str, Any]
        A JSON-style dictionary containing the charge result and any errors.
    """
    batched_option = '--batched' if batched else '--not_batched'
    broken_up_option = '--broken_up' if broken_up else '--not_broken_up'
    batched_grid_option = '--batched_grid' if batched_grid else '--not_batched_grid'

    return _esp_requester(
        charge_model, 
        batched_option, 
        broken_up_option, 
        conformer_mol, 
        grid, 
        batched_grid_option,
        protein
    )

def prepare_json_outs(
    charge_result: subprocess.CompletedProcess,
    batched: bool,
    broken_up: bool
) -> Dict[str, Any]:
    """
    Process the subprocess result and produce a JSON-style output.

    Parameters
    ----------
    charge_result : subprocess.CompletedProcess
        The result of the subprocess call containing stdout and stderr.
    batched : bool
        Indicates whether batched mode was used.
    broken_up : bool
        Indicates whether broken-up mode was used.

    Returns
    -------
    Dict[str, Any]
        A dictionary with the ESP results and any error messages.
    """
    output = charge_result.stdout.decode()
    error = charge_result.stderr.decode()

    if not batched:
        if not broken_up:
            try:
                esp, grid_out = output.split('OO')
                json_response = {
                    'esp_result': esp.strip(),
                    'grid': grid_out.strip(),
                    'error': error
                }
            except ValueError:
                json_response = {
                    'result': output.strip(),
                    'error': error
                }
        else:
            try:
                monopole, dipole, quadropole, grid_out = output.split('OO')
                json_response = {
                    'monopole': monopole.strip(),
                    'dipole': dipole.strip(),
                    'quadropole': quadropole.strip(),
                    'grid': grid_out.strip(),
                    'error': error
                }
            except ValueError:
                json_response = {
                    'result': output.strip(),
                    'error': error
                }
    else:
        json_response = {
            'file_path': output.strip(),
            'error': error
        }

    logging.info("Response: %s", json_response)
    return json_response

def main():
    mol = (
        "\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n"
        "   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
        "  1  2  1  0\n"
        "  2  3  1  0\nM  END\n"
    )

    # Example: using the RIN model in non-batched, non-broken-up, ligand mode.
    result = handle_esp_request(
        charge_model='RIN',
        conformer_mol=mol,
        batched=False,
        broken_up=False,
        grid=None,
        batched_grid=False,
        protein=False  # Change to True if the input is protein data.
    )
    print(result)

if __name__ == '__main__':
    main()
