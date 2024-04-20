import yaml
from income.exception import IncomeException
import os,sys



def read_yaml_file(file_path:str) -> dict:
    """
    Reads a Yaml file and returns the contents as a dictionary.
    file_path:str
    """
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise IncomeException(e,sys) from e