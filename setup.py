from setuptools import setup, find_packages

setup(
    name="maison_property_api",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.3",
        "flask-sqlalchemy>=3.1.1",
        "flask-migrate>=4.0.5",
        "flask-cors>=4.0.0",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
    ],
) 