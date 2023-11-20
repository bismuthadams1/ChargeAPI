import subprocess
import requests
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
from source.charge_models import base_class, eem_model


app = Flask(__name__)

@app.route('/<charge_model>/<smiles>', methods = ['GET','POST'])
def handle_charge_request(charge_model, smiles):
    """
    handle 
    """
    json_data = request.json
    conformer =  json.loads(json_data)['conformer']
    match charge_model:
        case 'EEM':
            charge_list = EEM_charge_model(smiles, conformer)
            return jsonify({'charge_list': charge_list})
        case 'MBIS':
            charge_list = MBIS_charge_model(smiles, conformer)
            return jsonify({'charge_list': charge_list})
        case _:
            raise NameError


def EEM_charge_model(smiles, conformer):
    """
    Existing EEM model in openbabel. Run charge model in own environment.
    """
    subprocess.run(['conda','activate','open_babel'])
    charge_list = eem_model(smiles, conformer)
    return charge_list

def MBIS_charge_model():
    ...

def ESPALOMA_charge_model():
    ...

def main():
    data = {
        "conformer": "CONFORMER_DATA"
    }

    json_data = json.dumps(data)
    app.handle_charge_request('HOH/EEM', json = json_data)

if __name__ == '__main__':
    main()