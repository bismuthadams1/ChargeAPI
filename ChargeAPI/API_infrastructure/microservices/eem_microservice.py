from flask import Flask, request, jsonify
from ChargeAPI.charge_models.eem_model import EEM_model


app = Flask(__name__)
eem_model = EEM_model()

#TODO 

@app.route('/calculate_charge', methods=['POST'])
def calculate_charge():
    json_data = request.json()
    # conformer_mol = json_data['conformer_mol']
    conformer_mol = json_data.get('conformer_mol')
    batched = json_data.get('batched', False)

    # Initialize the EEM model and perform calculations
    # EEM_Model initialization and calculation logic here...

    charges = eem_model(conformer_mol)

    # Return the calculated charges or result
    return jsonify({'charge_result': charges})

def main(ip):
    from waitress import serve
    serve(app, host="0.0.0.0", port=5001)


if __name__ == "__main__":
    main()
