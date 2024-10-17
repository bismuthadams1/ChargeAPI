"""
Requires Nagl MBIS model environment : https://github.com/jthorton/nagl-mbis
"""


import os
# Check if the module is imported for environment checking
if os.environ.get("IMPORT_CHECK") == "1":
    ENV_NAME = "naglmbis"  # Only define the environment name
    # Stop further execution of the module
    MODULE = "MBIS_Model_charge"
else:
    #used for execution
    from naglmbis.models import load_charge_model
    from base_class  import ExternalChargeModel
    from openff.toolkit.topology import Molecule
    import rdkit
    import subprocess
    import argparse

    class MBIS_Model_charge(ExternalChargeModel):

        _name = "naglmbis_wb_water_charge"
        def __init__(self, ftype="json"):
            super().__init__()
            self.file_type = ftype
            self.charge_model = load_charge_model(charge_model="nagl-gas-esp-wb-2A")

        def __call__(self,  conformer_mol: str, batched: bool, file_method: bool = False) -> list[int] | None:
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
                list containing charges for the molecule or filepath to charges for each conformer
            """
            
            return super().__call__(conformer_mol = conformer_mol, batched = batched)

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
    parser.add_argument('--conformer', type=str, help='Conformer mol')
    parser.add_argument('--batched', help='Batch charges or not', action='store_true')
    parser.add_argument('--not_batched', help='Batch charges or not', dest='batched', action='store_false')
    parser.set_defaults(batched = False)

    args = parser.parse_args()

    mbis_model = MBIS_Model_charge()
    charges = mbis_model(conformer_mol = args.conformer, batched = args.batched) 
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~
    print(charges)
    #ESSENTIAL TO PRINT THE CHARGES TO STDOUT~~~~