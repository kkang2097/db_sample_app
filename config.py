from dotenv import load_dotenv
import os 
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
FRONTEND_PW = os.getenv('FRONTEND_PW')
ZILLIZ_KEY = os.getenv('ZILLIZ_KEY')
ZILLIZ_URI = os.getenv('ZILLIZ_URI')