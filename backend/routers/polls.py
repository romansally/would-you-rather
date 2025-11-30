from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import Poll, PollCreate
from db import get_session
from typing import Literal
from pydantic import BaseModel

# Requesting Models
class VoteRequest(BaseModel):
    choice: Literal["a","b"]


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

@router.get(
    "/",
    response_model=list[Poll]
)
def list_polls(
    session: Session = Depends(get_session),
):
    '''
    Retrieve all active polls from the database.
    Returns an empty list if no polls exist.
    '''
    
    # Build the query to select all Poll records
    statement = select(Poll).where(Poll.is_active == True)
    
    # Execute the query and get all results
    polls = session.exec(statement).all()
    
    return polls

@router.get(
    "/{poll_id}",
    response_model=Poll,
)
def get_poll(
    poll_id: int,
    session: Session = Depends(get_session)
):
    '''
    Retrieve a single active poll by its ID.
    Returns 404 if the poll doesn't exist or is inactive 
    '''
    poll = session.get(Poll, poll_id)
    
    if poll is None or not poll.is_active:
        raise HTTPException(status_code=404, detail="Poll not found")

    return poll

@router.post(
    "/{poll_id}/vote",
    response_model = Poll,
)
def vote_on_poll(
    poll_id: int,
    vote: VoteRequest,
    session: Session = Depends(get_session),
):
    '''
    Cast a vote on a poll. 
    Increments votes_a or votes_b based on choice.
    '''
    poll = session.get(Poll, poll_id)
    
    if poll is None or not poll.is_active:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    # Increment the appropriate vote counter
    if vote.choice == "a":
        poll.votes_a += 1
    else:
        poll.votes_b += 1
    
    session.add(poll)
    session.commit()
    session.refresh(poll)
    
    return poll