from fastapi import FastAPI, Request, Depends
from functools import wraps, lru_cache
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import config

load_dotenv()
app = FastAPI()

#CORS setup (cross-origin thingies)
origins = [
    "http://localhost:8000",
    "http://localhost:54957",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Cache the MongoDB client connection
@lru_cache()
def get_db_client():
  #Connect to mongodb client
  return MongoClient(config.MONGO_URI)

#Need an auth wrapper!
def auth_required(func):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    #TODO: do stuff here (ie. check header for auth, but we should do this wayyyy later...)

    #We need our generated token string as the auth :)
    #Optimally we have some assert statement here...
    print(kwargs['request'].headers)

    return await func(*args, **kwargs)
  return wrapper

#Dummy HTTP request sample
@app.get('/')
@auth_required
async def root(request: Request):
  #return {'example': 'This is an example', 'data': config.FRONTEND_PW}
  return {'example': 'This is an example', 'data': 'fooled you'}

#
#DB requests start here :)
#

#Check MongoDB connection
@app.get('/checkdb')
@auth_required
async def check_db(request: Request, client: MongoClient = Depends(get_db_client)):
  retVal = client.admin.command('ping')
  print("Pinged your deployment. You successfully connected to MongoDB!")
  return retVal


#Get user
#This should actually be a POST request
@app.get('/getuser')
@auth_required
async def get_user(request: Request, client: MongoClient = Depends(get_db_client)):
  # This is how to get a part of the header!
  #return request.headers['cookie']

  #Get the user, if not we just create one.
  return {'answer': 'helloooo'}

#RSS calls
@app.post('/add-rss-feed')
@auth_required
async def add_rss(request: Request, client: MongoClient = Depends(get_db_client)):

  #await some db action
  #TODO: Do this after specifying User stuff....
  #response = await something

  #Conditional response - true/false
  return {'answer': 'Feed added'}