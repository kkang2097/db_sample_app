from fastapi import FastAPI, Request, Depends, HTTPException
from functools import wraps, lru_cache
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import InsertOne
import uvicorn
from dotenv import load_dotenv
import urllib.robotparser as urp
from fastapi.middleware.cors import CORSMiddleware
import config
from .api_utils import *
import requests as req
from datetime import datetime as dt

#Load environment variables
load_dotenv()

#Load app
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

@lru_cache()
def get_req_session():
  return req.Session()

@lru_cache()
def get_url_parser():
  return urp.RobotFileParser()

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
def add_rss(rss_name: str, rss_url: str, request: Request, client: MongoClient = Depends(get_db_client), rp= Depends(get_url_parser)):
  #If URL is not valid, raise an error...
  if not url_is_valid(rss_url):
    raise HTTPException(status_code=404, detail='URL not valid')
  if not can_scrape(rss_url, rp):
    raise HTTPException(status_code=418, detail='Cannot scrape this URL!')

  #Try finding the RSS Feed URL
  user_coll = client['data']['rss_feeds']
  outcome = user_coll.find_one({'_id': rss_url})

  #Get the user, if not we just create one.
  if(outcome == None):
    outcome = user_coll.insert_one({'_id': rss_url, 'name': rss_name, 'date_added': dt.now()})
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

#Dummy function for scheduled RSS master collection reset
#TODO: Turn this into a DAG, deploy a Docker container
@app.get('/data_scheduled')
@auth_required_sync
def dummy_scheduled_job(request: Request, client: MongoClient = Depends(get_db_client), req_session = Depends(get_req_session)):
  #If we finish, we can return True
  #Else, we can return False

  #Collect and parse all RSS feeds, put in master collection for posts

  #Grab the master RSS post collection, put into each individual collection
  bulk_list=[]

  try:
    user_coll = client['data']['rss_feeds']
    posts_coll = client['data']['posts']
    all_feeds = user_coll.find({})
    #Get all feeds
    for f in all_feeds:
      feed_url=f['_id']
      articles = get_articles(feed_url, req_session)
      #Get all articles in 1 feed
      for a in articles:
        title = a.find('title').text
        link = a.find('link').text
        published = a.find('pubDate').text
        description = a.find('description').text
        #TODO: Get fulltext of each article
        fulltext = get_fulltext(link, req_session)
        #TODO: Bulk add articles to MongoDB
        bulk_list.append(InsertOne({
          '_id': title,
          'link': link,
          'published': published,
          'description': description
        }))
        break
      #It's a good idea to place a breakpoint here for debugging
      break
  except BaseException as inst:
    print("Oh no, /data_scheduled JOB FAILED.")
  return True

#TODO: Data Labeling using Embedding Model
@app.get('/label_scheduled')
@auth_required_sync
def embedding_labels(request: Request, client: MongoClient = Depends(get_db_client)):

  #Label each post in DB

  return