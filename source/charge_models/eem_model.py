"""
   Existing EEM 2015 model available in OpenBabel https://open-babel.readthedocs.io/en/latest/Charges/charges.html
"""

from base_class import ExternalChargeModel
import openbabel

class EEM_model(ExternalChargeModel):

    def __init__(self, ftype="json"):
        super().__init__()
        self.file_type = ftype

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

    _name = "eem2015dn"
    def __call__(self,  mapped_smiles: str, conformer: np.ndarray, file_method = False):
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
        return super().__call__(tagged_smiles, conformer)

    

"""TODO
if __name__ == "__main__":
    # Define argparse setup for command line execution
    parser = argparse.ArgumentParser(description='EEM charge model arguments')
    parser.add_argument('mapped_smiles', type=str, help='Mapped SMILES representation')
    parser.add_argument('conformer', type=str, help='Conformer file path')

    args = parser.parse_args()
    eem_model = EEM_charge_model()
    eem_model(args.mapped_smiles, args.conformer) 
"""



