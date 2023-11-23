import subprocess
import tempfile
from multiprocessing import Process
import json
import numpy as np
import os


def handle_charge_request(charge_model: str, smiles: str, conformer: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    conformer = conformer.tolist()

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        #find full file path of tempfile
        conformer_file = os.path.dirname(temp_file.name)
    
        # Write conformer data to the temporary file
        json.dump(conformer, temp_file)

        match charge_model:
            case 'EEM':
                script_path = os.path.abspath('../charge_models/eem_model.py')
                cmd = (
                    f"conda run -n openbabel python {script_path} {smiles} {conformer_file}"
                )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
            case 'MBIS':
                cmd = (
                            f"conda run -n nagl-mbis python -m ../charge_models/mbis_model.py {smiles} {conformer_file}"
                        )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
            case _:
                raise NameError


def main():

    conformer = np.array([[-0.78900161, -0.19816432, -0.        ],
       [-0.00612716,  0.39173634, -0.        ],
       [ 0.79512877, -0.19357202,  0.        ]])

    json_charges = handle_charge_request(charge_model = 'EEM', smiles = '[H:1][O:2][H:3]', conformer = conformer)

if __name__ == '__main__':
    main()