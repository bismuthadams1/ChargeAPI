"""Existing EEM 2015 model available in OpenBabel https://open-babel.readthedocs.io/en/latest/Charges/charges.html
"""

from ChargeAPI.charge_models.base_class import ExternalChargeModel
from openbabel import openbabel as ob
from openbabel import pybel
import argparse
import subprocess
import numpy as np
import logging
import tempfile
from openff.units import unit
from openff.units.openmm import from_openmm, to_openmm
from openff.toolkit.topology import Molecule


#supress openff warnings
#logging.getLogger("openff").setLevel(logging.CRITICAL)
logging.basicConfig(filename='charge_api.log', level=logging.DEBUG)

class EEM_model(ExternalChargeModel):

    def __init__(self, ftype="json"):
        super().__init__()
        self.file_type = ftype

    _name = "eem2015dn"
    def check_code_availability(self):
        """Check external code can be run
        """

        self.available = False

        # Rudimentary check for openbabel conda environment
        output = subprocess.run(["conda", "info", "--envs"], capture_output=True)
        for line in output.stdout.decode().split("\n"):
                if line:
                    if line.split()[0] == "openbabel":
                        self.available = True

        return self.available

    def __call__(self,  conformer_file_path: str, file_method: bool = False):
        """Get charges for molecule.

        Parameters
        ----------
        mapped_smiles: mapped smiles 
            Molecule to run charge calculation on
        conformer: np.ndarray (n_atoms, 3)
            co
        file_type: str
            Type of file to output charges to [default = json]
        file_method: bool
            Some charge models require temporary files to be written and read, others use python objects stored in internal memory
        Returns
        -------
        charge_files: List of str
            Files containing charges for each molecule
        """
        return super().__call__(conformer_file_path)
    
    def convert_to_charge_format(self, conformer_file_path: str):
        """Convert openff molecule to appropriate format on which to assign charges

        Parameters
        ----------
        conformer_file_path: string
            File path to the mol to conver to appropriate format
        
        Returns
        -------
        ob_mol
           Open babel molecule
        
        """
        #read file is an iterator so can read multiple eventually
        ob_mol = next(pybel.readfile('mol',conformer_file_path))
      #  logging.info(f'the openbabel molecule is {ob_mol}')
        ob_mol = ob_mol.OBMol
        return ob_mol
    
    def assign_charges(self, ob_mol: pybel.Molecule):
        """Assign charges according to charge model selected

        Parameters
        ----------
        ob_mol: generic python object depending on the charge model
            Charge model appropriate python object on which to assign the charges

        Returns
        -------
        partial_charges: list of partial charges 
        """
        charge_model = ob.OBChargeModel.FindType("eem2015bn")
        charge_model.ComputeCharges(ob_mol)
        charges = [atom.GetPartialCharge() for atom in ob.OBMolAtomIter(ob_mol)]
       # logging.info(f'the charges coming out of assign_charges are: {charges}')
        return charges

if __name__ == "__main__":
    # Define argparse setup for command line execution
    parser = argparse.ArgumentParser(description='EEM charge model arguments')
    parser.add_argument('conformer', type=str, help='Conformer file path')
    args = parser.parse_args()
    #logging.info(f'the file path is: {args}')

    eem_model = EEM_model()
    charges = eem_model(conformer_file_path = args.conformer) 
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~
    print(charges)
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~



