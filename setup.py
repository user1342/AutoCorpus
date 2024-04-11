from setuptools import setup

setup(
    name='AutoCorpus',
    version='0.1',
    install_requires=[
        'argparse',
        'rich',
        'setuptools',
        'huggingface_hub',
        'numpy',
        'pyyaml',
        'torchvision',
        'torchaudio',
        'bitsandbytes',
        'accelerate',
        'transformers',
        'torch'
    ],
    entry_points={
        'console_scripts': [
            'AutoCorpus = AutoCorpus.auto_corpus:run'
        ]
    }
)