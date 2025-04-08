from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-jose==3.3.0",
        "passlib==1.7.4",
        "bcrypt==4.0.1",
        "python-multipart==0.0.6",
        "pydantic==2.4.2",
        "sqlalchemy==2.0.23",
        "python-dotenv==1.0.0",
        "motor==3.3.1",
        "pymongo==4.6.0",
        "email-validator==2.1.0.post1",
        "redis==5.0.1",
    ],
) 