"""
Requires Nagl MBIS model environment : https://github.com/jthorton/nagl-mbis
"""

from naglmbis.models import load_charge_model
from base_class import ExternalChargeModel
from openff.toolkit.topology import Molecule
import rdkit
import subprocess
import argparse

class MBIS_Model(ExternalChargeModel):
   
    def __init__(self, ftype="json"):
        super().__init__()
        self.file_type = ftype
        self.charge_model = load_charge_model(charge_model="nagl-v1-mbis")

    _name = "naglmbis"

    def check_code_availability(self):
        """Check external code can be run
        """

        self.available = False

        # Rudimentary check for openbabel conda environment
        output = subprocess.run(["conda", "info", "--envs"], capture_output=True)
        for line in output.stdout.decode().split("\n"):
                if line:
                    if line.split()[0] == "naglmbis":
                        self.available = True

        return self.available

    def convert_to_charge_format(self, conformer_mol: str):

        rdkit_conformer = rdkit.Chem.rdmolfiles.MolFromMolBlock(conformer_mol, removeHs = False)
        return rdkit_conformer
    
    def assign_charges(self, rdkit_conformer: Molecule):

        charges = self.charge_model.compute_properties(rdkit_conformer)["mbis-charges"]
        charges = charges.flatten().tolist()
        return charges


if __name__ == "__main__":
    # Define argparse setup for command line execution
    parser = argparse.ArgumentParser(description='MBIS charge model arguments')
    parser.add_argument('conformer', type=str, help='Conformer mol')
    args = parser.parse_args()

    mbis_model = MBIS_Model()
    charges = mbis_model(conformer_mol = args.conformer) 
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~
    print(charges)
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~