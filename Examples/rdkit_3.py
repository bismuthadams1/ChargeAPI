from openff.toolkit.topology import Molecule
import rdkit
from rdkit import Chem
from openff.recharge.grids import GridSettingsType, GridGenerator
from openff.recharge.grids import LatticeGridSettings, MSKGridSettings

molblock = """RDKit          2D


  3  2  0  0  0  0  0  0  0  0999 V2000
    1.2990    0.7500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0
  2  3  1  0
M  END
"""


rdkit_conformer = Chem.rdmolfiles.MolFromMolBlock(molblock, removeHs = False)
openff_mol = Molecule.from_rdkit(rdkit_conformer, allow_undefined_stereo=True)
print(openff_mol.conformers[0])
print(openff_mol)
grid_settings = MSKGridSettings(
        type="msk", density=2.0
    )
grid = GridGenerator.generate(openff_mol, openff_mol.conformers[0], grid_settings)
print(grid)