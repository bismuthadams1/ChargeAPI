"""
Requires Nagl MBIS model environment : https://github.com/jthorton/nagl-mbis
"""

from naglmbis.models import load_volume_model, load_charge_model
from base_class import ExternalChargeModel


class MBIS_Model(ExternalChargeModel):
    ...

