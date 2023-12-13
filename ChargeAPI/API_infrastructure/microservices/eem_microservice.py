from flask import Flask, request, jsonify
from ChargeAPI.charge_models.eem_model import EEM_model

app = Flask(__name__)

eem_model = EEM_model()


@app.route('/calculate_charge', methods=['POST'])
def calculate_charge():
    json_data = request.get_json()
    conformer_mol = json_data['conformer_mol']

    # Initialize the EEM model and perform calculations
    # EEM_Model initialization and calculation logic here...

    charges = eem_model(conformer_mol)

    # Return the calculated charges or result
    return jsonify({'charge_result': charges})


if __name__ == "__main__":
    ...
