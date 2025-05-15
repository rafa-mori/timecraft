from setuptools import setup, find_packages

setup(
    name="timecraft",
    version="0.1.0",
    author="Rafael Mori",
    author_email="faelmori@gmail.com",
    description="TimeCraft - A Python package for time series analysis and forecasting.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/faelmori/timecraft",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "plotly",
        "prophet",
        "requests",
        "jupyter",
        "notebook",
        "pyodbc",
        "jinja2",
        "mysql-connector-python",
        "pymongo",
        "cx_Oracle",
        "xarray",
        "sqlalchemy",
        "kaleido"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

