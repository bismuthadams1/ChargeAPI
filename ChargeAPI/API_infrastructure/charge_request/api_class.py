import subprocess
import requests
import tempfile
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
import os
#import logging
import ChargeAPI

app = Flask(__name__)
#logging.basicConfig(filename='charge_api.log', level=logging.DEBUG)

@app.route('/charge/<charge_model>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str, batched: bool = False) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    Parameters
    ---------
    charge_model: str
        Charge model to chose from the switch statement

    Returns
    -------
    json: json
        Json dictionary of calculation results, including errors.
    """
    json_data = request.get_json()
    json_data = json.loads(json_data)
    #extract the data from the json
    conformer_mol = json_data['conformer_mol']

    batched = json_data.get('batched', False)  # Defaults to False if not provided
    
    if batched:
        batched = '--batched'
    else:
        batched = '--not_batched'

    match charge_model:
            case 'EEM':
                script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/eem_model.py'
                #replace with requests json_charges = requests.post('http://127.0.0.1:5001/charge/EEM', json = json_data)

                cmd = (
                    f"conda run -n openbabel python {script_path} --conformer '{conformer_mol}' {batched}"
                )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                return prepare_json_outs(charge_result)
            case 'MBIS':
                script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/mbis_model.py'
                cmd = (
                        f"conda run -n nagl-mbis python -m {script_path}  --conformer '{conformer_mol}' --batched {batched}"
                       )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                return prepare_json_outs(charge_result)
            case _:
                raise NameError
         

@app.route('/shutdown', methods=['POST'])
def shutdown() -> str:
    """
    Shut down the API
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

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
        'charge_result': charge_result_list,
        'error': charge_result.stderr.decode()  # Include the error message if any
    }
    # Return the charge result as a list and the JSON response   
     
    return jsonify(json_response)

def main():
    #run the app
    from waitress import serve
    from microservices import eem_microservice, mbis_microservice
    ip = 5000
    serve(app, host="0.0.0.0", port=ip)
    eem_microservice.main(ip)
   # mbis_microservice.main(ip)


if __name__ == '__main__':
    main()