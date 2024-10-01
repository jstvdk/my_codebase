from setuptools import setup, find_packages

setup(
    name='muonpipe',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Specify your dependencies here
        # Example:
        'numpy>=1.19.2',
        'pandas>=1.1.3',
        'matplotlib>=3.3.2',
        'astropy>=4.0',
    ],
)