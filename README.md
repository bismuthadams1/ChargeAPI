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

`

`

 When called in non-batched mode, a JSON is 

The API will handle each charge model in its own environment. 
All charge model environments are detailed in the environment.yml file. The API_env environment should be used to run the environment.
Other environments included in the environment will handle the charge models.

## Installation

The API works by running each charge model in its own environment. 


#TODO add installation instructions here