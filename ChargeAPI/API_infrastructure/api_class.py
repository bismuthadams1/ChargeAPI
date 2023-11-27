import subprocess
import requests
import tempfile
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
import os

app = Flask(__name__)

@app.route('/charge/<charge_model>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    json_data = request.get_json()
    json_data = json.loads(json_data)
    conformer = json_data['conformer']
    #conformer = conformer.flatten().tolist()
    tagged_smiles = json_data['tagged_smiles']
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
       
    # Write conformer data to the temporary file
    json.dump(conformer, temp_file)
    temp_file.flush()
    
    #find full file path of tempfile
    conformer_file_path = temp_file.name

    match charge_model:
            case 'EEM':
                script_path = os.path.abspath('../ChargeAPI/ChargeAPI/charge_models/eem_model.py')
                cmd = (
                    f"conda run -n openbabel python {script_path} {tagged_smiles} {conformer_file_path}"
                )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                os.remove(conformer_file_path)
                charge_result_list = charge_result.stdout.decode()  # Convert the output to a list if it's a string
                # Create JSON response
                json_response = {
                    'charge_result': charge_result_list,
                    'error': charge_result.stderr.decode()  # Include the error message if any
                }
                # Return the charge result as a list and the JSON response
                return jsonify(json_response)
            case 'MBIS':
                script_path = os.path.abspath('../ChargeAPI/ChargeAPI/charge_models/mbis_model.py')
                cmd = (
                            f"conda run -n nagl-mbis python -m {script_path} {tagged_smiles} {conformer_file_path}"
                        )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                os.remove(conformer_file_path)
                charge_result_list = charge_result.stdout.decode()  # Convert the output to a list if it's a string
                  # Create JSON response
                json_response = {
                    'charge_result': charge_result_list,
                    'error': charge_result.stderr.decode()  # Include the error message if any
                }
                # Return the charge result as a list and the JSON response
                return jsonify(json_response)            
            case _:
                raise NameError
         

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


def main():
    app.run(debug=True)
    # data = {
    #     "conformer": "[-0.78900161, -0.19816432, -0.,-0.00612716,  0.39173634, -0., 0.79512877, -0.19357202,  0.]",
    #     "tagged_smiles":"[H:1][O:2][H:3]",
    #     "units":"angstrom"
    # }

    # json_data = json.dumps(data)
    # #in another application this would bejson_charges = app.handle_charge_request('http://127.0.0.1:5000/[H:1][O:2][H:3]/EEM', json = json_data)

    # json_charges = requests.post('http://127.0.0.1:5000/charge/EEM', json = json_data)

if __name__ == '__main__':
    main()