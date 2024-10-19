from setuptools import setup, find_packages

setup(
    name="bentoo-utils",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bentoo=overlay.main:main',
        ],
    },
    install_requires=[
        # Add any required dependencies here
    ],
)