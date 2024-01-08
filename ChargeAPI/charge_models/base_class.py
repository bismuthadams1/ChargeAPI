import subprocess
import tempfile
import json
import os
import logging 
import numpy as np
import tempfile

from rdkit import Chem
#from openff.toolkit.topology import Molecule
#from openff.units import unit

from abc import abstractmethod

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)
#logging.basicConfig(filename='charge_api.log', level=logging.DEBUG)

# EXT_CHARGE_MODELS = {}

class ExternalChargeModel:
    """Base class for external charge models
    """
    subclasses = {}

    _name = None
    def __init_subclass__(cls, *args, **kwargs):
        """
        Catch any new external charge models (all external charge models must inherit
        from this base class) and add them to the dict of external charge models.
        """
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls._name] = cls

    def __init__(self):
        """Initialise External charge model"""

    def check_code_availability(self):
        """Check external code can be run
        """

    @abstractmethod
    def __call__(self, conformer_mol: str, file_method = False, batched = False) -> list[int]  : #| None | str
        """Get charges for molecule.

        Parameters
        ----------
        conformer_file_path: str
            if batched == True, this is the file path to the temporary file 
            containing the conformer. If batched == False, this will just be
            mol string. 
        file_type: str
            Type of file to output charges to [default = json]
        file_method: bool
            Some charge models require temporary files to be written and read, others use python objects stored in internal memory
        batched: bool
            Batch
        Returns
        -------
        charges: List of int
            list containing charges for the molecule or filepath to charges for each conformer
            
        """
        if not batched:
            logging.info('not batched option chosen')

            charge_format = self.convert_to_charge_format(conformer_mol)
            #if the charge model requires generation and reading of files to produce charges
            if file_method:
                file_path = self.generate_temp_files(charge_format)
                charge_file_path = self.run_external_code(file_path)
                charges = self.read_charge_output(charge_file_path)
            #other charge model types will produce charges based on python objects in internal memory
            else:
                charges = self.assign_charges(charge_format)
            return charges

        else:
            logging.info(' batched option chosen')

            #make dictionary from json file
            mol_dictionary = self.molfile_to_dict(conformer_mol)
            for mol in mol_dictionary.items():
                charge_format = self.convert_to_charge_format(mol[1])
                charges = self.assign_charges(charge_format)
                mol_dictionary[mol[0]] = charges
            #write charges dictionary to file
            charge_file = f"{conformer_mol.strip('.json')}_charges.json"
            with open(charge_file,"w+") as outfile:
                json.dump(mol_dictionary, outfile, indent=2)
                #charge_file_path = os.path.abspath(charge_file)
            return charge_file



    def convert_to_charge_format(self, conformer_mol: str):
        """Convert openff molecule to appropriate format on which to assign charges

        Parameters
        ----------
        conformer_mol: string
            String to mol file
        
        Returns
        -------
        Charge_format
            Appropriate charge format to assign the partial charges 
        
        """

    def molfile_to_dict(self, conformer_file_path: str):
        """Convert json molfile to 
        
        """
        with open(conformer_file_path, 'r') as conformer_file:
            mol_dictionary = json.load(conformer_file)

        return mol_dictionary

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

    def generate_temp_files(self, charge_format: any):
        """Generate the temporary files required to run charge model

        Parameters
        ----------
        charge format: any
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
