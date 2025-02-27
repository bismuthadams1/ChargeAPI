import subprocess
import tempfile
from multiprocessing import Process
import json
import numpy as np
from typing import LiteralString, Literal
import os
import logging
import ChargeAPI

CHARGE_MODELS = Literal[
    'EEM',
    'MBIS',
    'MBIS_CHARGE',
    'MBIS_WB_GAS_CHARGE',
    'MBIS_WB_GAS_CHARGE_DIPOLE',
    'MBIS_WB_WATER_CHARGE',
    'MBIS_WB_WATER_CHARGE_DIPOLE',
    'MBIS_WB_WATER_CHARGE_DIPOLE_ESP',
    'MBIS_WB_GAS_ESP_2A',
    'MBIS_WB_GAS_ESP_15A',
    'MBIS_WB_GAS_ESP_DEFAULT',
    ]

model_locations = {
    'EEM' : '/charge_models/eem_model.py',
    'MBIS': '/charge_models/mbis_model.py',
    'MBIS_CHARGE': '/charge_models/mbis_model_charges.py',
    'MBIS_WB_GAS_CHARGE': '/charge_models/mbis_wb_gas_model_charges.py',
    'MBIS_WB_GAS_CHARGE_DIPOLE':'/charge_models/mbis_wb_gas_model_charges_dipole.py',
    'MBIS_WB_WATER_CHARGE':'/charge_models/mbis_wb_water_model_charges.py',
    'MBIS_WB_WATER_CHARGE_DIPOLE':'/charge_models/mbis_wb_water_model_charges_dipole.py',
    'MBIS_WB_WATER_CHARGE_DIPOLE_ESP':'/charge_models/mbis_wb_water_model_charges_dipole_esp_default.py',
    'MBIS_WB_GAS_ESP_2A':'/charge_models/mbis_wb_gas_esp_2A.py',
    'MBIS_WB_GAS_ESP_15A':'/charge_models/mbis_wb_gas_esp_15A.py',
    'MBIS_WB_GAS_ESP_DEFAULT':'mbis_wb_gas_charges_dipole_esp_default.py',
}

def _charge_requester(
    charge_model: CHARGE_MODELS,
    batched: LiteralString['--batched','--not_batched'],
    protein: bool,
    conformer_mol: str,
    ) -> dict[str,any]:
    
    if protein:
        print('protein mode')
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdb') as tmp_file:
            tmp_file.write(conformer_mol)
            input = tmp_file.name  # This is the file path we'll pass on.
    else:
        print('ligand mode')
        input = conformer_mol
        
    script_path = os.path.join(
        os.path.dirname(ChargeAPI.__file__),
        model_locations[charge_model]
    )

    # Build the command, passing the temporary file name as the argument.
    cmd = [
        "conda", "run", "--no-capture-output", "-n", "naglmbis", "python", script_path,
        "--conformer", input, batched  # Now passing the tmp file instead of '-'
    ]
            # Run the subprocess (note: we no longer use 'input=' since the script will read the file).
    charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Optionally, delete the temporary file after use.
    if protein:
            os.remove(input)
            
    return prepare_json_outs(charge_result)

    
    

def handle_charge_request(charge_model: str, conformer_mol: str, batched: bool = False, protein = False) -> dict[str,any, None]:
    """
    handle the charge request and run the correct charge model. Batched option accepts a JSON of molecule names and their
    corresponding forms in molblocks. 
    """
    if batched:
        batched = '--batched'
    else:
        batched = '--not_batched'

    try:
        result = _charge_requester(
            charge_model=charge_model,
            batched=batched,
            protein=protein,
            conformer_mol=conformer_mol
        )
        return result
    except KeyError:
        
        raise Exception("charge model does not exist")
        

def prepare_json_outs(charge_result: subprocess.CompletedProcess) -> json:
    """
    grabs data from subprocess and produces a json of the output
    Paramters
    --------
    charge_result:  subprocess.CompletedProcess
        Result of the subprocess run command in/out/error info
    """
    charge_result_list = charge_result.stdout.decode()  # Convert the output to a list of strings
    # Create JSON response
    json_response = {
        'charge_result': charge_result_list.strip('\n\n'),
        'error': charge_result.stderr.decode()  # Include the error message if any
    }
    logging.info(json_response)
    # Return the charge result as a list and the JSON response    
    return json_response    


def main():
    mol = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    json_result = handle_charge_request(
        charge_model = 'MBIS_WB_GAS_ESP_DEFAULT', 
        conformer_mol = mol,
        batched=False
    )
    print(json_result)

if __name__ == '__main__':
    main()
