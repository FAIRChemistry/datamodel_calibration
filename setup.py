import setuptools
from setuptools import setup

setup(
    name="calibration_data",
    version="0.0.1",
    description="Datamodel, handling calibration data from UV-Vis and HPLC measurements",
    url="https://github.com/FAIRChemistry/calibration_data",
    author="Haeussler, Max",
    author_email="st171427@stud.uni-stuttgart.de",
    packages=setuptools.find_packages(),
    install_requires=[
    "sdrdm @ git+https://github.com/JR-1991/software-driven-rdm.git",
    ]
)
