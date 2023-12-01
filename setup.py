import setuptools
from setuptools import setup

setup(
    name="CaliPytion",
    version="0.2",
    description="Data model and standard curve functionalities for calibration data",
    url="https://github.com/FAIRChemistry/calibration_data",
    author="Haeussler, Max",
    author_email="max.haeussler@ibtb.uni-stuttgart.de",
    packages=setuptools.find_packages(),
    install_requires=[
        "lmfit",
        "numpy",
        "pandas",
        "sympy",
        "plotly",
        "pydantic==1.8.2",
        "scipy",
        "nbformat",
        "setuptools",
        "matplotlib",
    ],
)
