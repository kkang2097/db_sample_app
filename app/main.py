from fastapi import FastAPI, Request, Depends, HTTPException
from functools import wraps, lru_cache
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import re
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
def auth_required_async(func):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    #TODO: do stuff here (ie. check header for auth, but we should do this wayyyy later...)

    #We need our generated token string as the auth :)
    #Optimally we have some assert statement here...
    print(kwargs['request'].headers)

    return await func(*args, **kwargs)
  return wrapper

def auth_required_sync(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    #TODO: do stuff here (ie. check header for auth, but we should do this wayyyy later...)

    #We need our generated token string as the auth :)
    #Optimally we have some assert statement here...
    print(kwargs['request'].headers)

    return func(*args, **kwargs)
  return wrapper

#Dummy HTTP request sample
@app.get('/')
@auth_required_async
async def root(request: Request):
  #return {'example': 'This is an example', 'data': config.FRONTEND_PW}
  return {'example': 'This is an example', 'data': 'fooled you'}

#
#DB requests start here :)
#

#Check MongoDB connection
@app.get('/checkdb')
@auth_required_async
async def check_db(request: Request, client: MongoClient = Depends(get_db_client)):
  retVal = client.admin.command('ping')
  print("Pinged your deployment. You successfully connected to MongoDB!")
  return retVal


#Get user
#This should actually be a POST request
@app.post('/getuser')
@auth_required_sync
def get_user(username: str, request: Request, client: MongoClient = Depends(get_db_client)):
  #Input:
  # Username - String
  #Output:
  # Success (hopefully)

  user_coll = client['data']['users']
  outcome = user_coll.find_one({'_id': username})

  #Get the user, if not we just create one.
  if(outcome == None):
    outcome = user_coll.insert_one({'_id': username,
                                    'subs': {'dummy_sub1': 'dummy_desc', 'dummy_sub2': 'dummy_desc'},
                                    'feed': {'dummy_post': 'dummy_body', 'dummy_post2': 'dummy_body2'},
                                    'curated': {'dummy_post': 'dummy_body', 'dummy_post2': 'dummy_body2'}})
    outcome = user_coll.find_one({'_id': username})
    return outcome
  else:
    return outcome

#RSS calls
@app.post('/add-rss-feed')
@auth_required_sync
def add_rss(rss_name: str, rss_url: str, request: Request, client: MongoClient = Depends(get_db_client)):

  #Validate URL first...
  regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  
  is_valid = re.match(regex, rss_url) is not None

  #If URL is not valid, raise an error...
  if not is_valid:
    raise HTTPException(status_code=404, detail='URL not valid')

  #Try finding the RSS Feed URL
  user_coll = client['data']['rss_feeds']
  outcome = user_coll.find_one({'_id': rss_url})

  #Get the user, if not we just create one.
  if(outcome == None):
    outcome = user_coll.insert_one({'_id': rss_url, 'name': rss_name})
    outcome = user_coll.find_one({'_id': rss_url})
    return outcome
  else:
    return outcome

@app.post('/add-rss-sub')
@auth_required_sync
def add_rss_sub(rss_name: str, username: str, request: Request, client: MongoClient = Depends(get_db_client)):
  #TODO: Add RSS subscriptions to a specific user


  #Find the RSS feed in our master collection


  #If valid, push to our user's RSS subscriptions



  return None