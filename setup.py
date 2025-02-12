from setuptools import setup, find_packages

setup(
    name="maison_property_api",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-cors",
        "python-dotenv",
    ],
) 