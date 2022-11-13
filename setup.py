import setuptools
from setuptools import setup

setup(
    name="datamodel_calibration",
    version="0.0.1",
    description="Datamodel, handling calibration data from UV-Vis measurements",
    url="https://github.com/FAIRChemistry/calibration_data",
    author="Haeussler, Max",
    author_email="st171427@stud.uni-stuttgart.de",
    packages=setuptools.find_packages(),
    install_requires=[
    "sdRDM @ git+https://github.com/JR-1991/software-driven-rdm.git",
    ]
)
