import subprocess
import requests
import tempfile
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
from source.charge_models import base_class, eem_model

app = Flask(__name__)

@app.route('/<smiles>/<charge_model>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str, smiles: str) -> dict[str,any]:
    """
    handle the charge request and run the correct charge model
    """
    json_data = request.json
    conformer = json_data.get('conformer')

    """
    TODO
    Proposed new structure to add tomorrow
     with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        conformer_file = temp_file.name

        # Write conformer data to the temporary file
        json.dump(conformer, temp_file)

        # Call the specific charge model function with the temporary file path
        if charge_model == 'EEM':
            cmd = (
                f"conda run -n eem-env python -m EEM_charge_model {smiles} {conformer_file}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return jsonify({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
        elif charge_model == 'MBIS':
            cmd = (
                f"conda run -n nagl-mbis python -m MBIS_charge_model {smiles} {conformer_file}"
            )
            charge_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return jsonify({'charge_result': charge_result.stdout.decode(), 'error': charge_result.stderr.decode()})
        else:
            raise NameError("Invalid charge model")
    
    """

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


# def EEM_charge_model(tagged_smiles: str, conformer: str, units: str) -> list[float]:
#     """
#     Existing EEM model in openbabel. Run charge model in own environment.
#     """
#     #will launch a new process but won't be able to pass info from API. conda ENVNAME executable, add code in 
#     #will need to pass info between with tmp files or can print out data. stdout. Linux pipes. subprocess.run -> return statement, loads everything the print statement has written. 
#     subprocess.run(['conda','activate','openbabel'])
#     charge_list = eem_model(tagged_smiles, conformer, units = units)
#     return charge_list

# def MBIS_charge_model():
#     ...

# def ESPALOMA_charge_model():
#     ...

def main():
    data = {
        "conformer": "[-0.78900161, -0.19816432, -0.,-0.00612716,  0.39173634, -0., 0.79512877, -0.19357202,  0.]",
        "units":"angstrom"
    }

    json_data = json.dumps(data)
    #in another application this would bejson_charges = app.handle_charge_request('http://127.0.0.1:5000/[H:1][O:2][H:3]/EEM', json = json_data)

    json_charges = app.handle_charge_request('[H:1][O:2][H:3]/EEM', json = json_data)

if __name__ == '__main__':
    main()