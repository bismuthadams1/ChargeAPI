import subprocess
import tempfile
import json
import os
from rdkit import Chem
import logging 

from abc import abstractmethod

LOGGER = logging.getLogger(__name__)

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
    def __call__(self, molecules: list[Chem.Mol], file_type: str = "json"):
        """Get charges for molecule.

        Parameters
        ----------
        molecules: List of Chem.Mol
            Molecule to run charge calculation on
        file_type: str
            Type of file to output charges to [default = json]

        Returns
        -------
        charge_files: List of str
            Files containing charges for each molecule
            
        """
        files_to_run = self.create_tmp_files(molecules)
        output_files = self.run_external_code(files_to_run)
        charges = self.read_charge_output(output_files)
        if file_type == "json":
            charge_files = self.to_json(charges, molecules)
        else:
            raise NotImplementedError

        return charge_files


    def run_external_code(self, molecule_files: list[str]):
        """Run external charge model to generate charges
        
        Parameters
        ----------
        molecule_files: String
            Files containing molecules to input to the external code

        Returns
        -------
        returns file containing charges
        """

    def read_charge_output(charge_files: list[str]):
        """Read charges from files produced by external code
        
        Parameters
        ----------
        charge_files: String
            Files containing output from external file, from which charges can be read
        
        Returns
        -------
        returns charges as a list of lists (charges for each atom for each molecule)
        """

    def to_json(self, charges: list[list[float]], molecules: list[Chem.Mol]):
        """Write charges to json file

        Parameters
        ----------
        charges: List of List of float
            Lists of charges, each set of charges being a list of floating point values
        molecules: List of rdkit.Chem.Mol objects
            List of molecules, each molecule should have had Name property set
            
        Returns
        -------
        json_file: List of str
          files containing each set of charges
        """
        
        json_file = get_valid_id_name() + "_charges.json"

        charge_dict = {}
        for charge_set, molecule in zip(charges, molecules):
            mol_name = molecule.GetProp("_Name")
            if mol_name == "reference":
                charge_dict = charge_set
            else:
                charge_dict[mol_name] = charge_set
        

        LOGGER.info(charge_dict)

        json.dump(charge_dict, open(json_file, "w"))

        return json_file