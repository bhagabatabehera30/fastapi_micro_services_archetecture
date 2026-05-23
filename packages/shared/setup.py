from setuptools import setup, find_packages

setup(
    name="shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "sqlalchemy==2.0.25",
        "python-jose[cryptography]==3.3.0",
        "bcrypt>=4.0.0",
        "pydantic-settings==2.1.0",
    ],
)
