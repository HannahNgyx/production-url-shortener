from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import random
import string
from pydantic import BaseModel # for validation of the input data
import os # for environment variables 
from contextlib import asynccontextmanager #FastAPI protocol requires async context manager 
import psycopg # for PostgreSQL database connection
from dotenv import load_dotenv # for loading environment variables
from urllib.parse import urlparse # for parsing the URL

load_dotenv() # load the environment variables 

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Before app starts, setup the database
   conn = psycopg.connect(os.environ["DATABASE_URL"])
   conn.execute("CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, original_url TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())")
   conn.commit()
   conn.close()
   
   yield

app = FastAPI(lifespan=lifespan)

class URL(BaseModel):
    original_url: str
    short_url: str
    code: str

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/urls")   
def create_url(url: str):
    url = url.strip() 
    if not url:
        raise HTTPException(status_code=422, detail="Empty URL")
    if len(url) > 2048: # check if the URL is too long
        raise HTTPException(status_code=422, detail="This URL is too long")
    parsed_url = urlparse(url) # parse the URL
    if not parsed_url.netloc or parsed_url.scheme not in ["http", "https"]: # check if the URL is valid
        raise HTTPException(status_code=422, detail="Invalid URL")
    code = generate_code() 
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    conn.execute(
        "INSERT INTO urls (code, original_url) VALUES (%s, %s)",
        (code, url),
    )
    conn.commit()
    conn.close()
    return URL(original_url=url, short_url=f"http://localhost:8000/{code}", code=code)

@app.get("/{code}")
def redirect_to_url(code: str):
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        row = conn.execute(
            "SELECT original_url FROM urls WHERE code = %s",
            (code,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Unknown code")
    return RedirectResponse(status_code=302, url=row[0])
