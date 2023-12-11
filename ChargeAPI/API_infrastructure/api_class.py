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
def handle_charge_request(charge_model: str) -> dict[str,any]:
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

    match charge_model:
            case 'EEM':
                script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/eem_model.py'
                cmd = (
                    f"conda run -n openbabel python {script_path} '{conformer_mol}'"
                )
                charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                return prepare_json_outs(charge_result)
            case 'MBIS':
                script_path = f'{os.path.dirname(ChargeAPI.__file__)}/charge_models/mbis_model.py'
                cmd = (
                            f"conda run -n nagl-mbis python -m {script_path}  '{conformer_mol}'"
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
    #logging.info(f'assigne charges run with charges: {charges}')
     
    return jsonify(json_response)

def main():
    #run the app
    #app.run(debug=True,threaded=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)


if __name__ == '__main__':
    main()