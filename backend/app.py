from fastapi import FastAPI
from routers import polls

# Create the main FastAPI app
app = FastAPI(title="Would You Rather API")

# Include the polls router
app.include_router(polls.router)

# Root endpoint to confirm the API is running
@app.get("/")
def root():
    return {"message": "Would You Rather API is running"}
