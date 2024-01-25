# main file of the game eg. ludo, carom, solitaire etc
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import leaderboard

app = FastAPI()

# origin helps specify which hosts to allow 
# acces to the server
origins = [
    'http://localhost:3000'
    ]

# Enable CORS for all origins - security check between requests to
# ensure no unauthorized person gets access
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials = True,
    allow_methods=['*'],
    allow_headers=['*'],

)

# Include routers
app.include_router(leaderboard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
