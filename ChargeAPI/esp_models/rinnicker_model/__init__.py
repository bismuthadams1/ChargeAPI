#TODO find a way, in a similar manner to molevaluate, of listing the external charge models. 
# from ChargeAPI.charge_models.base_class import EXT_CHARGE_MODELS
import subprocess
import pkgutil
import importlib
import os
from .base_class import ExternalESPModel

EXT_CHARGE_MODELS = {}

os.environ["IMPORT_CHECK"] = "1"

def is_env_available(env_name):
    """Check if a specific conda environment is available"""
    output = subprocess.run(["conda", "info", "--envs"], capture_output=True)
    for line in output.stdout.decode().split("\n"):
        if line and line.split()[0] == env_name:
            return True
    return False

for _, module_info, _ in pkgutil.iter_modules(__path__):
    module_name = module_info
    module = importlib.import_module('.' + module_name, __package__)
    env_name = getattr(module, 'ENV_NAME', None)
    charge_model = getattr(module, 'MODULE', None)
    if is_env_available(env_name):
        EXT_CHARGE_MODELS[charge_model] = env_name

os.environ.pop("IMPORT_CHECK", None)