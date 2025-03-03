from setuptools import setup, find_packages

setup(
    name="browser-time-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.1.4",
        "matplotlib>=3.8.2",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "browser-time-analyzer=src.main:main",
        ],
    },
    author="Simon Sikkeland",
    description="A tool to analyze browser history and calculate time distribution across profiles",
    python_requires=">=3.8",
) 