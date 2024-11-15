from setuptools import setup, find_packages

setup(
    name='icecube_cluster',
    version='00.01',
    description='IceCube cluster tools',
    author='Tom Stuttard',
    author_email='thomas.stuttard@nbk.ku.dk',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
)