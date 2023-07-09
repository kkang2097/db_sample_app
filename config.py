from dotenv import load_dotenv
import os 
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
FRONTEND_PW = os.getenv('FRONTEND_PW')