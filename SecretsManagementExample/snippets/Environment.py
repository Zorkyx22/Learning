from dotenv import load_dotenv
import os

load_dotenv(".secrets")

credentials = {
    'username': os.getenv("USERNAME"),
    'password': os.getenv("PASSWORD"),
}
api_key = os.getenv('API_KEY')

def authenticate_somewhere(credentials, api_key):
    pass