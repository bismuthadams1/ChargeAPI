import subprocess
import tempfile
from multiprocessing import Process
import json
import numpy as np
import os
import logging

from ChargeAPI.charge_models.eem_model import EEM_model

logging.basicConfig(filename='charge_api.log', level=logging.DEBUG)

def handle_charge_request(charge_model: str, conformer_xyz: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    #flatten to list for json
    #conformer = conformer.flatten().tolist()

    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.xyz')
       
    # Write conformer data to the temporary file
    temp_file.write(conformer_xyz)
    temp_file.flush()
    
    #find full file path of tempfile
    conformer_file_path = temp_file.name

    match charge_model:
        case 'EEM':
            script_path = os.path.abspath('../ChargeAPI/charge_models/eem_model.py')
            cmd = (
                f"conda run -n openbabel python {script_path} {conformer_file_path}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            # eem_model = EEM_model()
            # result = eem_model(conformer_file_path=conformer_file_path) 
            os.remove(conformer_file_path)

            return prepare_json_outs(charge_result)
            #return result
        case 'MBIS':
            script_path = os.path.abspath('../ChargeAPI/charge_models/mbis_model.py')
            cmd = (
                        f"conda run -n nagl-mbis python -m {script_path} {conformer_file_path}"
                    )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            os.remove(conformer_file_path)
            return prepare_json_outs(charge_result)
        case _:
            raise NameError

def prepare_json_outs(charge_result: subprocess.CompletedProcess) -> json:
    """
    grabs data from subprocess and produces a json of the output
    Paramters
    --------
    charge_result:  subprocess.CompletedProcess
        Result of the subprocess run command in/out/error info
    """
    charge_result_list = charge_result.stdout.decode()  # Convert the output to a list if it's a string
    logging.info(f'the charge result list is:{charge_result_list}')
    # Create JSON response
    json_response = {
        'charge_result': charge_result_list,
        'error': charge_result.stderr.decode()  # Include the error message if any
    }
    logging.info(json_response)
    # Return the charge result as a list and the JSON response        
    return json_response