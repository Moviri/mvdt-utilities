from setuptools import setup, find_packages

setup(
    name="mvdt_utilities",
    version="0.1.0",
    description="Moviri utilities for Dynatrace extension development.",
    author="Moviri",
    author_email="dynatrace_extensions@moviri.com",
    url="https://github.com/Moviri/mvdt-utilities",
    packages=find_packages(),
    install_requires=['win32security', 'cachetools'], 
)