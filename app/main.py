from fastapi import FastAPI 
import uvicorn

app = FastAPI()

#Dummy HTTP request sample
@app.get('/')
async def root():
  return {'example': 'This is an example', 'data': 0}


#Need an auth wrapper!




#DB requests start here :)