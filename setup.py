from setuptools import setup, find_packages

setup(
    name='erc20_monitor',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'apache-airflow',
        'web3',
        'discord.py',
    ],
    entry_points={
        'console_scripts': [
            'erc20_monitor = erc20_monitor.main:main',
        ],
    },
)
