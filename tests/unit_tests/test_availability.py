from  ChargeAPI.charge_models import EXT_CHARGE_MODELS

def test_expected_models():
    EXPECTED_MODELS = {'EEM_model': 'openbabel', 'MBIS_Model': 'naglmbis', 'MBIS_Model_charge': 'naglmbis'}
    assert EXPECTED_MODELS == EXT_CHARGE_MODELS