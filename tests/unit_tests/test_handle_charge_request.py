from ChargeAPI.API_infrastructure.module_version import handle_charge_request
import ChargeAPI
from unittest.mock import patch, MagicMock
import pytest
import os


class TestHandleChargeRequest:
    mol  = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'

    #this replaces the subprocess call
    @patch('ChargeAPI.API_infrastructure.module_version.subprocess.run')
    def test_handle_charge_request_with_EEM(self, mock_run):

        mock_stdout = MagicMock()
        
        '[0.41073812213382016, -0.8164372902205344, 0.4056991680867142]'
        mock_stdout.configure_mock(
            **{"stdout":b"[0.41073812213382016, -0.8164372902205344, 0.4056991680867142]",
               "stderr":b""
            }
        )
        mock_run.return_value = mock_stdout

        charge_model = 'EEM'
        conformer_mol = self.mol
        expected_response = {'charge_result':'[0.41073812213382016, -0.8164372902205344, 0.4056991680867142]','error':''}

        charge_request = handle_charge_request(charge_model = charge_model, conformer_mol = conformer_mol, batched = False)
        assert charge_request == expected_response

    #this replaces the subprocess call
    @patch('ChargeAPI.API_infrastructure.module_version.subprocess.run')
    def test_handle_charge_request_with_MBIS(self, mock_run):

        mock_stdout = MagicMock()

        mock_stdout.configure_mock(
            **{"stdout":b"[0.4071686863899231, -0.8143373727798462, 0.4071686863899231]\n\n",
               "stderr":b""
            }
        )
        mock_run.return_value = mock_stdout
        charge_model = 'MBIS'
        conformer_mol = self.mol
        expected_response = {'charge_result':'[0.4071686863899231, -0.8143373727798462, 0.4071686863899231]','error':''}
        charge_request = handle_charge_request(charge_model = charge_model, conformer_mol = conformer_mol, batched = False)
        
        assert charge_request == expected_response
    
