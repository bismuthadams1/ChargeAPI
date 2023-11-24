import subprocess
import tempfile
from multiprocessing import Process
import json
import numpy as np
import os

def handle_charge_request(charge_model: str, smiles: str, conformer: np.ndarray) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    #flatten to list for json
    conformer = conformer.flatten().tolist()

    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
       
    # Write conformer data to the temporary file
    json.dump(conformer, temp_file)
    temp_file.flush()
    
    #find full file path of tempfile
    conformer_file_path = temp_file.name

    match charge_model:
        case 'EEM':
            script_path = os.path.abspath('../ChargeAPI/source/charge_models/eem_model.py')
            cmd = (
                f"conda run -n openbabel python {script_path} {smiles} {conformer_file_path}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
            # eem_model = EEM_model()
            # charges = eem_model(smiles, conformer_file_path) 
            return charges
        case 'MBIS':
            script_path = os.path.abspath('../ChargeAPI/source/charge_models/mbis_model.py')
            cmd = (
                        f"conda run -n nagl-mbis python -m {script_path} {smiles} {conformer_file_path}"
                    )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
        case _:
            raise NameError

    os.remove(conformer_file_path)

def main():

    conformer = np.array([[-0.78900161, -0.19816432, -0.        ],
       [-0.00612716,  0.39173634, -0.        ],
       [ 0.79512877, -0.19357202,  0.        ]])

    json_charges = handle_charge_request(charge_model = 'EEM', smiles = '[H:1][O:2][H:3]', conformer = conformer)

    print(json_charges)

if __name__ == '__main__':
    main()