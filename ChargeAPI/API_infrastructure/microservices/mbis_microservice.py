from flask import Flask, request, jsonify

from ChargeAPI.charge_models.mbis_model import MBIS_Model

app = Flask(__name__)

eem_model = MBIS_Model()

#TODO 

@app.route('/calculate_charge', methods=['POST'])
def calculate_charge():
    json_data = request.get_json()
    conformer_mol = json_data['conformer_mol']

    # Initialize the EEM model and perform calculations
    # EEM_Model initialization and calculation logic here...

    charges = eem_model(conformer_mol)

    # Return the calculated charges or result
    return jsonify({'charge_result': charges})

def main(ip):
    from waitress import serve
    serve(app, host="0.0.0.0", port=ip+1)


if __name__ == "__main__":
    main()
