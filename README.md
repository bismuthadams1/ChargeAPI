# ChargeAPI

The ChargeAPI was created to allow new charge models to be rapidly deployed across the platform in an environment agnostic manner. 

## General Use

API for handling charge requests for different charge models. Currently the user has two options for calling charge models:

1. A python module, located at `../ChargeAPI/API_infrastructure/module_version.py`. 
2. A http flask server, located at `../ChargeAPI/API_infrastructure/api_class.py`.

The python module is currently the 'faster' version, and is recommended for usage in python codes across the platform. 
The API can either be called in single pass mode or batched mode. The API currently accepts molecules in MolBlock format, where RDKit molecules
can readily be converted to MolBlock strings via `rdkit.Chem.rdmolfiles.MolToMolBlock`.

The API accepts molecules one-by-one or as a batch. In non-batched mode, the python module is called via:

```mol_block = '\n     RDKit          3D\n\n  3  2  0  0  0  0  0  0  0  0999 V2000\n   -0.7890   -0.1982   -0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.0061    0.3917   -0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n    0.7951   -0.1936    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0\n  2  3  1  0\nM  END\n'
    
json_result = ChargeAPI.API_infrastructure.module_version.handle_charge_request(charge_model = 'MBIS', 
                                        conformer_mol = mol,
                                        batched=False)
```
A JSON dictionary is then produced with the result, which can be parsed to a list:

```>> {'charge_result': '[0.4071686863899231, -0.8143373727798462, 0.4071686863899231]', 'error': ''}

charges_module =  json.loads(charges['charge_result'])
```

In batched-mode, again using the python module as an example, a path to a JSON containing all the MolBlocks you want to run. The keys in the JSON will correspond to the molecule names.
To illustrate this, here is a general example of how to produce the JSON:

```       
        mol_file = {}
        for mol in molecules:
            if mol.HasProp("_Name"):
                mol_file[mol.GetProp("_Name")] = rdkit.Chem.rdmolfiles.MolToMolBlock(mol)
            else:
                mol_file[get_valid_id_name()] =  rdkit.Chem.rdmolfiles.MolToMolBlock(mol)

        file_name = "mols.json"
        #write molblocks to json
        with open(file_name,"w+") as outfile:
            json.dump(mol_file, outfile, indent=2)
            file_path = os.path.abspath(file_name)
```
We then supply the `file_path` as an argument to the module.

```charge_file_path = ChargeAPI.API_infrastructure.module_version.handle_charge_request(charge_model = "MBIS",
                                                        conformer_mol = file_path, 
                                                        batched = True)
```

The output is then a JSON containing the charges in order of the atoms supplied in the MolBlock, with keys corresponding to the same names in the input.

The HTTP version is still in partial and will be updated later. 

## Installation

The API works by running each charge model in its own environment. Current charge models are contained in the yml files naglmbis.yml and openbabel.yml. 
Before the API can be used across the platform, it is essential that all the environments are accessible on the machine you are running on. 
It is recommended that the openbabel environment is installed via the instructions here https://pypi.org/project/openbabel/. 

The API environment is intended to be as lightweight as possible, and is the main environment which the charge models are processed.

The whole ChargeAPI package can be installed by navigating to the local ChargeAPI directory and running:

`pip install -e .`


#TODO add installation instructions here