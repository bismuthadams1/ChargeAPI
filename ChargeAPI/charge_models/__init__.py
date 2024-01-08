#TODO find a way, in a similar manner to molevaluate, of listing the external charge models. 
# from ChargeAPI.charge_models.base_class import EXT_CHARGE_MODELS
import subprocess
import pkgutil
import importlib
import os
from .base_class import ExternalChargeModel


env_names = {}
EXT_CHARGE_MODELS = {}
available_ext_models = {}

os.environ["IMPORT_CHECK"] = "1"

def is_env_available(env_name):
    """Check if a specific conda environment is available"""
    output = subprocess.run(["conda", "info", "--envs"], capture_output=True)
    for line in output.stdout.decode().split("\n"):
        if line and line.split()[0] == env_name:
            return True
    return False

for _, module_info, _ in pkgutil.iter_modules(__path__):
    print(module_info)
    module_name = module_info
    module = importlib.import_module('.' + module_name, __package__)
    env_name = getattr(module, 'ENV_NAME', None)
    charge_model = getattr(module, 'MODULE', None)
    if is_env_available(env_name):
        EXT_CHARGE_MODELS[charge_model] = env_name

# for module_name, env_name in env_names.items():
#     if is_env_available(env_name):
#         model_module = importlib.import_module('.' + module_name, __package__)
#         for attr_name in dir(model_module):
#             attr = getattr(model_module, attr_name)
#             if isinstance(attr, type) and issubclass(attr, ExternalChargeModel):
#                 EXT_CHARGE_MODELS[attr.__name__] = attr

# Reset or clear the flag after imports
os.environ.pop("IMPORT_CHECK", None)