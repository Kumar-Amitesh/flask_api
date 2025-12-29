from flask import Flask
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

app = Flask(__name__)
