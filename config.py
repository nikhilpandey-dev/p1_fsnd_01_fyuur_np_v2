import os
from helpers import sqlalchemy_config
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enabled debug mode.
DEBUG = True

# Connected to the database
params: str = sqlalchemy_config(filename="./database.ini")
print("Database URI after calling config object: ")
print(params)

# IMPLEMENTED DATABASE URL
SQLALCHEMY_DATABASE_URI = params

SQLALCHEMY_TRACK_MODIFICATIONS = False

