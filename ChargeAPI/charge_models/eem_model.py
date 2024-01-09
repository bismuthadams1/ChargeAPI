"""Existing EEM 2015 model available in OpenBabel https://open-babel.readthedocs.io/en/latest/Charges/charges.html
"""

import os
# Check if the module is imported for environment checking
if os.environ.get("IMPORT_CHECK") == "1":
    ENV_NAME = "openbabel"  # Only define the environment name
    # Stop further execution of the module
    MODULE = "EEM_model"
else:
    #used for execution
    from ChargeAPI.charge_models.base_class import ExternalChargeModel
    from openbabel import openbabel as ob
    from openbabel import pybel
    import argparse
    import numpy as np

    class EEM_model(ExternalChargeModel):
        
        _name = "eem2015dn"
        def __init__(self, ftype="json"):
            super().__init__()
            self.file_type = ftype

        def __call__(self,  conformer_mol: str, batched: bool, file_method: bool = False) -> list[int]:
            """Get charges for molecule.

            Parameters
            ----------
            mapped_smiles: mapped smiles 
                Molecule to run charge calculation on
            conformer_mol: str
                conformer in mol format
            file_type: str
                Type of file to output charges to [default = json]
            file_method: bool
                Some charge models require temporary files to be written and read, others use python objects stored in internal memory
            Returns
            -------
            charge_files: List of str
                Files containing charges for each molecule
            """
            
            return super().__call__(conformer_mol = conformer_mol, batched = batched)
        
        def convert_to_charge_format(self, conformer_mol: str) -> ob.OBMol:
            """Convert openff molecule to appropriate format on which to assign charges

            Parameters
            ----------
            conoformer_mol: string
                File path to the mol to convert to appropriate format
            
            Returns
            -------
            ob_mol
            Open babel molecule
            
            """
            #read file is an iterator so can read multiple eventually
            ob_mol = pybel.readstring('mol',conformer_mol)
            ob_mol = ob_mol.OBMol
            return ob_mol
        
        def assign_charges(self, ob_mol: pybel.Molecule) -> list[float]:
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
            #logging.info(f'assigne charges run with charges: {charges}')

            return charges
    
if __name__ == "__main__":
    # Define argparse setup for command line execution
    parser = argparse.ArgumentParser(description='EEM charge model arguments')
    parser.add_argument('--conformer', type=str, help='Conformer mol')
    parser.add_argument('--batched', help='Batch charges or not', action='store_true')
    parser.add_argument('--not_batched', help='Batch charges or not', dest='batched', action='store_false')    
    parser.set_defaults(batched = False)

    args = parser.parse_args()
    eem_model = EEM_model()
    charges = eem_model(conformer_mol = args.conformer, batched = args.batched) 
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~
    print(charges)
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~




