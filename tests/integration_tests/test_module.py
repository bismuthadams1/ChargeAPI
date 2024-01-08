import pytest
from ChargeAPI.API_infrastructure import module_version
import json

def test_EEM():
    expected_charges = [0.41073812213382016, -0.8164372902205344, 0.4056991680867142]
    mol  = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    json_result = module_version.handle_charge_request(charge_model = 'EEM', 
                                                    conformer_mol = mol,
                                                    batched=False)
    assert json.loads(json_result['charge_result']) == expected_charges

def test_mbis():
    expected_charges = [0.4071686863899231, -0.8143373727798462, 0.4071686863899231]
    mol  = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    json_result = module_version.handle_charge_request(charge_model = 'MBIS', 
                                                    conformer_mol = mol,
                                                    batched=False)
    assert json.loads(json_result['charge_result']) == expected_charges

def test_mbis_charges():    
    expected_charges = [0.4147946834564209, -0.8295893669128418, 0.4147946834564209]
    mol  = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    json_result = module_version.handle_charge_request(charge_model = 'MBIS_CHARGE', 
                                                    conformer_mol = mol,
                                                    batched=False)
    assert json.loads(json_result['charge_result']) == expected_charges


