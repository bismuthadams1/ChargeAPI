from rdkit import Chem

# conformer_mol = """
#  RDKit          3D

#   3  2  0  0  0  0  0  0  0  0999 V2000
#    -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
#    -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
#     0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
#   1  2  1  0
#   2  3  1  0
# M  END
# """
conformer_mol ='\n     RDKit          2D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n    1.2990    0.7500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n   -1.2990    0.7500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'

print("Original MolBlock:\n", conformer_mol)

# Remove leading/trailing whitespace and any extra newlines
# cleaned_conformer_mol = conformer_mol.strip()

# print("Cleaned MolBlock:\n", conformer_mol)

# Convert the cleaned MolBlock string to an RDKit molecule
rdkit_conformer = Chem.rdmolfiles.MolFromMolBlock(conformer_mol, removeHs=False)

if rdkit_conformer:
    print("Conversion successful:", rdkit_conformer)
else:
    print("Conversion failed")
