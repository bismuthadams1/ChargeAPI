"""Existing EEM 2015 model available in OpenBabel https://open-babel.readthedocs.io/en/latest/Charges/charges.html
"""

import os

from numpy import ndarray
# Check if the module is imported for environment checking
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
if os.environ.get("IMPORT_CHECK") == "1":
    ENV_NAME = "rinnicker"  # Only define the environment name
    # Stop further execution of the module
    MODULE = "RIM_model"
else:
    #used for execution
    from base_class import ExternalESPModel #ChargeAPI
    from MultipoleNet import load_model, build_graph_batched, D_Q
    from openff.units import unit
    import argparse
    import rdkit
    import numpy as np
    from openff.recharge.grids import GridSettingsType, GridGenerator
    from openff.recharge.grids import LatticeGridSettings, MSKGridSettings
    from openff.toolkit import Molecule

    class RIN_model(ExternalESPModel):
        
        _name = "rinnicker"
        def __init__(self, ftype="json"):
            super().__init__()
            self.file_type = ftype
            self.dtype = np.float32
            self.esp_model = load_model()
            self.AU_ESP = unit.atomic_unit_of_energy / unit.elementary_charge

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
        
        def convert_to_charge_format(self, conformer_mol: str) -> tuple[np.ndarray,list[str]]:
            """Convert openff molecule to appropriate format on which to assign charges

            Parameters
            ----------
            conformer_mol: string
                File path to the mol to convert to appropriate format
            
            Returns
            -------
            coordinates, elements: tuple   
                Tuple of coordinates and elements
            
            """
            #read file is an iterator so can read multiple eventually
            rdkit_conformer = rdkit.Chem.rdmolfiles.MolFromMolBlock(conformer_mol, removeHs = False)
            elements = [a.GetSymbol() for a in rdkit_conformer.GetAtoms()]
            coordinates = rdkit_conformer.GetConformer(0).GetPositions().astype(self.dtype)
            return coordinates, elements  
        
        def build_grid(self, conformer_mol: str) -> ndarray:
            """Builds the grid on which to assign the esp

            Parameters
            ----------
            co
            
            """

            rdkit_conformer = rdkit.Chem.rdmolfiles.MolFromMolBlock(conformer_mol, removeHs = False)
            openff_mol = Molecule.from_rdkit(rdkit_conformer)
            grid_settings = MSKGridSettings(
                    type="msk", density=2.0
                )
            grid = GridGenerator.generate(openff_mol, openff_mol.conformers[0], grid_settings)
            # grid = grid.to(unit.angstrom)

            return grid
        
        def assign_esp(self, coordinates_elements: tuple[np.ndarray,str], grid: unit.Quantity) -> list[float,float]:
            """Assign charges according to charge model selected

            Parameters
            ----------
            ob_mol: generic python object depending on the charge model
                Charge model appropriate python object on which to assign the charges

            Returns
            -------
            partial_charges: list of partial charges 
            """
            (coordinates, elements) = coordinates_elements
            monopoles, dipoles, quadrupoles = self.esp_model.predict(coordinates, elements)
            #multipoles with correct units
            monopoles_quantity = monopoles.numpy()*unit.e
            dipoles_quantity = dipoles.numpy()*unit.e*unit.angstrom
            quadropoles_quantity = quadrupoles.numpy()*unit.e*unit.angstrom*unit.angstrom
            coordinates_ang = coordinates * unit.angstrom
            monopole_esp = self.calculate_esp_monopole_au(grid_coordinates=grid,
                                                atom_coordinates=coordinates_ang,
                                                charges = monopoles_quantity)
            dipole_esp = self.calculate_esp_dipole_au(grid_coordinates=grid,
                                            atom_coordinates=coordinates_ang,
                                            dipoles= dipoles_quantity)
            quadrupole_esp = self.calculate_esp_quadropole_au(grid_coordinates=grid,
                                            atom_coordinates=coordinates_ang,
                                            quadrupoles= quadropoles_quantity)
            #NOTE: ESP units, hartree/e and grid units are angstrom
            return (monopole_esp + dipole_esp + quadrupole_esp).m.flatten().tolist(), grid.m.tolist()
    
        def calculate_esp_monopole_au(self,
            grid_coordinates: unit.Quantity,  # N x 3
            atom_coordinates: unit.Quantity,  # M x 3
            charges: unit.Quantity,  # M
            ):
            """Generate the esp from the on atom monopole
            
            Parameters
            ----------
            grid_coordinates: unit.Quantity
                grid on which to build the esp on 

            atom_coordinates: unit.Quantity
                coordinates of atoms to build the esp  
            
            charges: unit.Quantity
                monopole or charges

            Returns
            -------
            monopole_esp: unit.Quantity
                monopole esp
            """
            #prefactor
            ke = 1 / (4 * np.pi * unit.epsilon_0) # 1/vacuum_permittivity, 1/(e**2 * a0 *Eh)

            #Ensure everything is in AU and correct dimensions
            charges = charges.flatten()
            grid_coordinates = grid_coordinates.reshape((-1, 3)).to(unit.bohr)  #Å to Bohr
            atom_coordinates = atom_coordinates.reshape((-1, 3)).to(unit.bohr)    #Å to Bohr
            #displacement and distance
            displacement = grid_coordinates[:, None, :] - atom_coordinates[None, :, :]  # N x M x 3 B
            distance = np.linalg.norm(displacement.m, axis=-1)*unit.bohr # N, M
            inv_distance = 1 / distance  #N, M

            esp = ke*np.sum(inv_distance * charges[None,:], axis=1)  # (N,M)*(1,M) -> (N,M) numpy broadcasts all charges. Over all atoms  =  Sum over M (atoms), resulting shape: (N,) charges broadcast over each N
            
            return esp.to(self.AU_ESP)

        def calculate_esp_dipole_au(self,
            grid_coordinates: unit.Quantity,  # N , 3
            atom_coordinates: unit.Quantity,  # M , 3
            dipoles: unit.Quantity,  # M , 3       
            ) -> unit.Quantity:
            """Generate the esp from the on atom dipoles
            
            Parameters
            ----------
            grid_coordinates: unit.Quantity
                grid on which to build the esp on 

            atom_coordinates: unit.Quantity
                coordinates of atoms to build the esp  
            
            dipoles: unit.Quantity
                dipoles or charges

            Returns
            -------
            dipoles_esp: unit.Quantity
                monopole esp
            """

            #prefactor
            ke = 1 / (4 * np.pi * unit.epsilon_0) # 1/vacuum_permittivity, 1/(e**2 * a0 *Eh)

            #Ensure everything is in AU
            dipoles = dipoles.to(unit.e*unit.bohr)
            grid_coordinates = grid_coordinates.reshape((-1, 3)).to(unit.bohr)  #Å to Bohr
            atom_coordinates = atom_coordinates.reshape((-1, 3)).to(unit.bohr)    #Å to Bohr

            displacement = grid_coordinates[:, None, :] - atom_coordinates[None, :, :]  # N , M , 3 
            distance = np.linalg.norm(displacement.m, axis=-1)*unit.bohr # N, M 
            inv_distance_cubed = 1 / distance**3 #1/B
            #Hadamard product for element-wise multiplication
            dipole_dot = np.sum(displacement * dipoles[None,:,:], axis=-1) # dimless * e.a

            esp = ke*np.sum(inv_distance_cubed* dipole_dot,axis=1) # e.a/a**2 

            return esp.to(self.AU_ESP)

        def calculate_esp_quadropole_au(self,
            grid_coordinates: unit.Quantity,  # N x 3
            atom_coordinates: unit.Quantity,  # M x 3
            quadrupoles: unit.Quantity,  # M N 
            ) -> unit.Quantity:
            """Generate the esp from the on atom quandropoles
            
            Parameters
            ----------
            grid_coordinates: unit.Quantity
                grid on which to build the esp on 

            atom_coordinates: unit.Quantity
                coordinates of atoms to build the esp  
            
            quandropoles: unit.Quantity
                dipoles or charges

            Returns
            -------
            quandropoles_esp: unit.Quantity
                monopole esp
            """

            #prefactor
            ke = 1 / (4 * np.pi * unit.epsilon_0) # 1/vacuum_permittivity, 1/(e**2 * a0 *Eh)
            #Ensure everything is in AU
            quadrupoles = quadrupoles.to(unit.e*unit.bohr*unit.bohr)    
            grid_coordinates = grid_coordinates.reshape((-1, 3)).to(unit.bohr)  #Å to Bohr
            atom_coordinates = atom_coordinates.reshape((-1, 3)).to(unit.bohr)    #Å to Bohr

            displacement = grid_coordinates[:, None, :] - atom_coordinates[None, :, :]  # N , M , 3 
            distance = np.linalg.norm(displacement.m, axis=-1)*unit.bohr # N, M 
            inv_distance = 1 / distance #1/B

            quadrupole_dot_1 = np.sum(quadrupoles[None,:,:] * displacement[:,:,None],axis=-1)
            quadrupole_dot_2 = np.sum(quadrupole_dot_1*displacement,axis=-1)
            esp = ke*np.sum((3*quadrupole_dot_2*(1/2 * inv_distance**5)),axis=-1)

            return esp.to(self.AU_ESP)

if __name__ == "__main__":
    # Define argparse setup for command line execution
    parser = argparse.ArgumentParser(description='RIN charge model arguments')
    parser.add_argument('--conformer', type=str, help='Conformer mol')
    parser.add_argument('--batched', help='Batch charges or not', dest='batched', action='store_true')
    parser.add_argument('--not_batched', help='Batch charges or not', dest='batched', action='store_false')    
    parser.set_defaults(batched = False)
   
    args = parser.parse_args()
    rin_model = RIN_model()
    #Esp currently in hartree/energy and grid in angstrom. 
    if not args.batched:
        values, esp_grid = rin_model(conformer_mol = args.conformer, batched = args.batched) 
        print(values, 'OO', esp_grid)
    else:
        file_path = rin_model(conformer_mol = args.conformer, batched = args.batched) 
        print(file_path)




