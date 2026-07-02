import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read_version()->str:
    with open(os.path.join(here, 'VERSION.txt'), encoding='utf-8') as f:
        return f.read().strip()

def read_readme()->str:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

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
    name='ebook2audiobook',
    version=read_version(),
    description='Convert eBooks to audiobooks with chapters and metadata',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/DrewThomasson/ebook2audiobook',
    author='Drew Thomasson',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=read_requirements(),
    python_requires='>=3.10',
)
