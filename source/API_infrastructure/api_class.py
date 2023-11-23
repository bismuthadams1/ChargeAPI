import subprocess
import requests
import tempfile
from flask import Flask, request, jsonify
from multiprocessing import Process
import json

app = Flask(__name__)

@app.route('/<smiles>/<charge_model>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str, smiles: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    json_data = request.json
    conformer = json_data.get('conformer')

    with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
        #find full file path of tempfile
        conformer_file = os.path.dirname(temp_file.name)
    
        # Write conformer data to the temporary file
        json.dump(conformer, temp_file)

        match charge_model:
            case 'EEM':
                cmd = (
                    f"conda run -n eem-env python -m ../charge_models/eem_model.py {smiles} {conformer_file}"
                )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return jsonify({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
            case 'MBIS':
                cmd = (
                            f"conda run -n nagl-mbis python -m ../charge_models/mbis_model.py {smiles} {conformer_file}"
                        )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return jsonify({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
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

    json_charges = requests.post('http://127.0.0.1:5000/[H:1][O:2][H:3]/EEM', json = json_data)

if __name__ == '__main__':
    main()