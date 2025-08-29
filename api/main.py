from dotenv import load_dotenv
load_dotenv()

from cachetools import TTLCache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, welcome, aws

# Init FastAPI
app = FastAPI(title='FastAPI-Google-AWS', version='1.0', root_path="/api")

# Create a sessions in-memory storage: 1000 sessions / users, 1 hour TTL (same TTL as JWTs)
app.state.sessions = TTLCache(maxsize=1000, ttl=3600)

# Allow your dev frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(auth.router)
app.include_router(welcome.router)
app.include_router(aws.router)

# Add root route
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello World!"}
