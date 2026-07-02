import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read_requirements()->list:
    requirements = []
    with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('./') or line.startswith('../'):
                continue
            requirements.append(line)
    return requirements

setup(
    install_requires=read_requirements(),
    packages=find_packages(exclude=['tests', 'tests.*']),
)
