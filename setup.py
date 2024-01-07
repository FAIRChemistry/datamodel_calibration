import setuptools
from setuptools import setup

setup(
    name="CaliPytion",
    version="0.3.0",
    description="Data model and standard curve functionalities for calibration data",
    url="https://github.com/FAIRChemistry/calibration_data",
    author="Haeussler, Max",
    author_email="max.haeussler@ibtb.uni-stuttgart.de",
    packages=setuptools.find_packages(),
    install_requires=[
        "lmfit",
        "numpy==1.24.4",
        "pandas",
        "sympy",
        "plotly",
        "pydantic",
        "scipy",
        "nbformat",
        "setuptools",
        "matplotlib",
    ],
)
