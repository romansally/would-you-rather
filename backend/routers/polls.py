from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import Poll, PollCreate
from db import get_session


# Create a router to group all poll-related endpoints
router = APIRouter(prefix="/polls", tags=["polls"])

# Simple health check route to confirm the polls router is working
@router.get("/health")
def health():
    return {"ok": True}

@router.post(
    "/",
    response_model=Poll,
    status_code=201
) 
def create_poll(
    poll_in: PollCreate,
    session: Session = Depends(get_session),
):
    # Convert the validated PollCreate input into a Poll DB model
    poll = Poll.model_validate(poll_in)

    # Add to the session and commit so it is saved in the database
    session.add(poll)
    session.commit()

    # Refresh to load generated fields like `id`
    session.refresh(poll)

    # Return the created poll
    return poll