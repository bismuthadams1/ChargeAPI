import pytest
from ChargeAPI.API_infrastructure import module_version
import json
import os

class SingleTests:
    mol  = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'

    def test_EEM(self):
        expected_charges = [0.41073812213382016, -0.8164372902205344, 0.4056991680867142]
        json_result = module_version.handle_charge_request(charge_model = 'EEM', 
                                                           conformer_mol = self.mol,
                                                           batched=False)
        assert json.loads(json_result['charge_result']) == expected_charges

    def test_mbis(self):
        expected_charges = [0.4071686863899231, -0.8143373727798462, 0.4071686863899231]
        json_result = module_version.handle_charge_request(charge_model = 'MBIS', 
                                                           conformer_mol = self.mol,
                                                           batched=False)
        assert json.loads(json_result['charge_result']) == expected_charges

    def test_mbis_charges(self):    
        expected_charges = [0.4147946834564209, -0.8295893669128418, 0.4147946834564209]
        json_result = module_version.handle_charge_request(charge_model = 'MBIS_CHARGE', 
                                                            conformer_mol = self.mol,
                                                            batched=False)
        assert json.loads(json_result['charge_result']) == expected_charges

class BatchedCharges:
    mol_file_path = os.path.abspath('./tests/data/mol_file.mol')

    @pytest.fixture
    def unpack_charge_file(self, file_path):
        charge_data = json.load(open(file_path))
        listed_data = [items[1] for items in charge_data.items()]
        return listed_data
    
    @pytest.fixture
    def read_data_file(self, file_path):
        with open(file_path, 'r') as file:
            data = json.loads(file.read())
        return data

    def test_EEM_batched(self):
        EEM_expected_data = os.path.abspath('./tests/data/EEM_batched.json')
        json_result = module_version.handle_charge_request(charge_model='EEM',
                                                           conformer_mol = self.mol_file_path,
                                                           batched=True)
        assert self.unpack_charge_file(json_result['charge_result']) == self.read_data_file(EEM_expected_data)