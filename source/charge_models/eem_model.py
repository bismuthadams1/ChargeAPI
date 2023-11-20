from base_class import ExternalChargeModel

class EEM_model(ExternalChargeModel):
   """
   Existing EEM 2015 model available in OpenBabel https://open-babel.readthedocs.io/en/latest/Charges/charges.html
   """
   def __init__(self, ftype="json"):
        super().__init__()
        self.file_type = ftype