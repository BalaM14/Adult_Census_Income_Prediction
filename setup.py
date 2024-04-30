from setuptools import setup,find_packages
from typing import List

PROJECT_NAME="income_predictor"
VERSION="0.0.4"
AUTHOR="Bala Murugan"
DESCRIPTION="This is a Incomee Predictor ML project"

REQUIREMENT_FILE_NAME="requirements.txt"
HYPHEN_E_DOT = "-e ."

def get_requirements_list() -> List[str]:
    
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list

setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    packages=find_packages(),                   #Here we are using this find_packages instead of housing is to check all the folders and wherever the __init__.py is there it will create a package
    install_requires=get_requirements_list()
)