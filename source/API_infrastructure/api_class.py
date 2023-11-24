import subprocess
import requests
import tempfile
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
import os

app = Flask(__name__)

@app.route('/charge/<smiles>/<charge_model>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str, smiles: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
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
                os.remove(conformer_file_path)
                return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
                # eem_model = EEM_model()
                # charges = eem_model(smiles, conformer_file_path) 
                # return charges
            case 'MBIS':
                script_path = os.path.abspath('../ChargeAPI/source/charge_models/mbis_model.py')
                cmd = (
                            f"conda run -n nagl-mbis python -m {script_path} {smiles} {conformer_file_path}"
                        )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                os.remove(conformer_file_path)
                return json.dumps({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
            case _:
                raise NameError


def main():
    #app.run(debug=True)
    data = {
        "conformer": "[-0.78900161, -0.19816432, -0.,-0.00612716,  0.39173634, -0., 0.79512877, -0.19357202,  0.]",
        "units":"angstrom"
    }

    json_data = json.dumps(data)
    #in another application this would bejson_charges = app.handle_charge_request('http://127.0.0.1:5000/[H:1][O:2][H:3]/EEM', json = json_data)

    json_charges = requests.post('http://127.0.0.1:5000/charge/[H:1][O:2][H:3]/EEM', json = json_data)

if __name__ == '__main__':
    main()