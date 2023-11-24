import subprocess
import tempfile
import json
import os
import logging 
import numpy as np
import tempfile


from rdkit import Chem
from openff.toolkit.topology import Molecule
from openff.units import unit

from abc import abstractmethod

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)

EXT_CHARGE_MODELS = {}

class ExternalChargeModel:
    """Base class for external charge models
    """

    _name = None

    def __init_subclass__(cls, *args, **kwargs):
        """
        Catch any new external charge models (all external charge models must inherit
        from this base class) and add them to the dict of external charge models.
        """
        super().__init_subclass__(**kwargs)
        if cls._name is not None:
            # Register new external charge model
            EXT_CHARGE_MODELS[cls._name] = cls

    def __init__(self):
        """Initialise External charge model"""

    def check_code_availability(self):
        """Check external code can be run
        """

    @abstractmethod
    def __call__(self, tagged_smiles: str, conformer_file_path: str, file_method = False):
        """Get charges for molecule.

        Parameters
        ----------
        mapped_smiles: mapped smiles 
            Molecule to run charge calculation on
        conformer_file_path: str
            file path to the conformer.
        file_type: str
            Type of file to output charges to [default = json]
        file_method: bool
            Some charge models require temporary files to be written and read, others use python objects stored in internal memory
        Returns
        -------
        charge_files: List of str
            Files containing charges for each molecule
            
        """
        conformer = self._file_to_conformer(conformer_file_path)
        openff_molecule = self.convert_to_openff_mol(tagged_smiles, conformer)
        #if the charge model requires generation and reading of files to produce charges
        if file_method:
            file_path = self.generate_temp_files(openff_molecule)
            charge_file_path = self.run_external_code(file_path)
            charges = self.read_charge_output(charge_file_path)
        #other charge model types will produce charges based on python objects in internal memory
        else:
            charge_format = self.convert_to_charge_format(openff_molecule)
            charges = self.assign_charges(charge_format)

        return charges

    def _file_to_conformer(self, conformer_file_path: str) -> np.ndarray:
        """Open file and provide conformer as np.ndarray

        Parameters
        ----------
        conformer_file_path: string
            File path of the temporary file containing the conformer
        Returns
        -------
        conformer: np.ndarray
            Conformer array of shape (n_atoms, 3)
        """
        with open(conformer_file_path, "r") as tempfile:
            tempfile.seek(0)
            conformer_string = tempfile.read()
            conformer = np.array(json.loads(conformer_string)).reshape(-1,3) 
            conformer = unit.Quantity(conformer, unit.angstrom)
            return conformer 


    def convert_to_openff_mol(self, tagged_smiles: str, conformer: unit.Quantity):
        """Convert the molecule to openff.Molecule format 
        
        Parameters
        ----------
        mapped_smiles: string
            Mapped smiles with indicies linked to the conformer
        conformer: np.ndarray (n_atoms,3)
            Conformer 
        
        Returns
        -------
        openff_molecule: openff_molecule format
            Files containing molecules, to be used in external code
        """
        openff_molecule = Molecule.from_mapped_smiles(tagged_smiles)
        openff_molecule.add_conformer(conformer)

        return openff_molecule

    def convert_to_charge_format(self, openff_molecule: 'Molecule'):
        """Convert openff molecule to appropriate format on which to assign charges

        Parameters
        ----------
        openff_molecule: openff.topology.Molecule
            Molecule to conver to appropriate format
        
        Returns
        -------
        Charge_format
            Appropriate charge format to assign the partial charges 
        
        """

    def assign_charges(self, charge_format: any):
        """Assign charges according to charge model selected

        Parameters
        ----------
        charge_format: generic python object depending on the charge model
            Charge model appropriate python object on which to assign the charges

        Returns
        -------
        partial_charges: list of partial charges 
        
        """

    def generate_temp_files(self, openff_molecule: 'Molecule'):
        """Generate the temporary files required to run charge model

        Parameters
        ----------
        openff_molecule: openff.topology.Molecule
            Molecule to convert to temporary file
        
        Returns
        -------
        file
            Temporary file to build charges off
        """

    def run_external_code(self, molecule_files: str):
        """Run external charge model to generate charges on molecule files
        
        Parameters
        ----------
        molecule_files: String
            Files containing molecules to input to the external code

        Returns
        -------
        returns file containing charges
        """


    def read_charge_output(charge_files: str):
        """Read charges from files produced by external code
        
        Parameters
        ----------
        charge_files: String
            Files containing output from external file, from which charges can be read
        
        Returns
        -------
        returns charges as a list of lists (charges for each atom for each molecule)
        """

    # def to_json(self, charges: list[float], molecule: list[Chem.Mol]):
    #     """Write charges to json file

    #     Parameters
    #     ----------
    #     charges: List of List of float
    #         Lists of charges, each set of charges being a list of floating point values
    #     molecules: List of rdkit.Chem.Mol objects
    #         List of molecules, each molecule should have had Name property set
            
    #     Returns
    #     -------
    #     json_file: List of str
    #       files containing each set of charges
    #     """
        
    #     json_file = + "_charges.json" #get_valid_id_name() 

    #     charge_dict = {}
    #     for charge_set, molecule in zip(charges, molecules):
    #         mol_name = molecule.GetProp("_Name")
    #         if mol_name == "reference":
    #             charge_dict = charge_set
    #         else:
    #             charge_dict[mol_name] = charge_set
        

    #     LOGGER.info(charge_dict)

    #     json.dump(charge_dict, open(json_file, "w"))

    #     return json_file