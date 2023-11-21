import subprocess
import requests
from flask import Flask, request, jsonify
from multiprocessing import Process
import json
from source.charge_models import base_class, eem_model

app = Flask(__name__)

@app.route('/<charge_model>/<smiles>', methods = ['GET','POST'])
def handle_charge_request(charge_model: str, smiles: str) -> dict[str,Any] | None:
    """
    handle 
    """
    # conformer = request.json['conformer']
    # if not request.json['units']:
    #     units = 'angstrom'
    

    match charge_model:
        case 'EEM':
            charge_list = EEM_charge_model(smiles, conformer)
            return jsonify({'charge_list': charge_list})
        case 'MBIS':
            charge_list = MBIS_charge_model(smiles, conformer)
            return jsonify({'charge_list': charge_list})
        case _:
            raise NameError


def EEM_charge_model(tagged_smiles: str, conformer: str, units: str) -> list[float]:
    """
    Existing EEM model in openbabel. Run charge model in own environment.
    """
    subprocess.run(['conda','activate','openbabel'])
    charge_list = eem_model(tagged_smiles, conformer, units = units)
    return charge_list

def MBIS_charge_model():
    ...

def ESPALOMA_charge_model():
    ...

def main():
    data = {
        "conformer": "array([[-0.78900161, -0.19816432, -0.        ],[-0.00612716,  0.39173634, -0.        ],[ 0.79512877, -0.19357202,  0.        ]])",
        "units":"angstrom"
    }

    json_data = json.dumps(data)
    app.handle_charge_request('[H:1][O:2][H:3]/EEM', json = json_data)

if __name__ == '__main__':
    main()