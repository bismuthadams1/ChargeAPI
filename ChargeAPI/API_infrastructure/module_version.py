import subprocess
import tempfile
from multiprocessing import Process
import json
import numpy as np
import os
import logging

from ChargeAPI.charge_models.eem_model import EEM_model
import ChargeAPI

#logging.basicConfig(filename='charge_api.log', level=logging.DEBUG)

def handle_charge_request(charge_model: str, conformer_mol: str, batched: bool = False) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    if batched:
        batched = '--batched'
    else:
        batched = '--not_batched'

    if charge_model == 'EEM':
            script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/eem_model.py'
            cmd = (
                f"conda run -n openbabel python {script_path} --conformer '{conformer_mol}' {batched}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return prepare_json_outs(charge_result)
    elif charge_model == 'MBIS':
            script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/mbis_model.py'
            cmd = (
                f"conda run -n naglmbis python {script_path} --conformer '{conformer_mol}'  {batched}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return prepare_json_outs(charge_result)
    else:
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
    json_result = handle_charge_request(charge_model = 'MBIS', 
                                        conformer_mol = mol,
                                        batched=False)
    print(json_result)

if __name__ == '__main__':
    main()