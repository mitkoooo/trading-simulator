from setuptools import setup, find_packages

setup(
    name="trading_simulator",
    description="A stock-exchange simulator with CLI and matching engine",
    author="Vadim Mitko",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
