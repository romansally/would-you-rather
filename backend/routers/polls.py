import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from models import Poll, PollCreate
from db import get_session
from typing import Literal
from pydantic import BaseModel
import random


# ==========================================
#  SECURITY DEPENDENCY
# ==========================================

def verify_admin(x_admin_token: str | None = Header(default=None)):
    """
    Verifies the X-Admin-Token header against the environment variable.
    
    Security Design:
    - Fails closed: If ADMIN_TOKEN is not set in .env, raise 500 (never allow access)
    - Returns 403 for invalid/missing tokens
    - Only allows access when token matches exactly
    """
    expected_token = os.getenv("ADMIN_TOKEN")
    
    # Safety net: If environment variable is missing, fail immediately
    # This prevents accidentally deploying without auth configured
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: ADMIN_TOKEN not set"
        )
    
    # Check if the provided token matches
    if x_admin_token != expected_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing admin token"
        )
    
    # Token is valid, allow request to proceed
    return True


# ==========================================
#  REQUEST/RESPONSE MODELS
# ==========================================

class VoteRequest(BaseModel):
    """Request body for voting on a poll."""
    choice: Literal["a", "b"]


# ==========================================
#  ROUTER SETUP
# ==========================================

router = APIRouter(prefix="/polls", tags=["polls"])


# ==========================================
#  PUBLIC ENDPOINTS (No Authentication)
# ==========================================

@router.get("/health")
def health():
    """Health check endpoint to verify the API is running."""
    return {"ok": True}


@router.get("/", response_model=list[Poll])
def list_active_polls(session: Session = Depends(get_session)):
    """
    PUBLIC ENDPOINT: List all active polls.
    
    This endpoint is used by the public voting UI (/play).
    Only returns polls where is_active=True.
    """
    statement = select(Poll).where(Poll.is_active == True)
    polls = session.exec(statement).all()
    return polls


@router.get("/random", response_model=Poll)
def get_random_poll(session: Session = Depends(get_session)):
    """
    PUBLIC ENDPOINT: Get a random active poll.
    
    Used by the "Surprise Me" feature in the public UI.
    Returns 404 if no active polls exist.
    """
    statement = select(Poll).where(Poll.is_active == True)
    polls = session.exec(statement).all()
    
    if not polls:
        raise HTTPException(
            status_code=404,
            detail="No active polls available"
        )
    
    return random.choice(polls)


@router.get("/{poll_id}", response_model=Poll)
def get_poll(
    poll_id: int,
    session: Session = Depends(get_session)
):
    """
    PUBLIC ENDPOINT: Get a specific active poll by ID.
    
    Returns 404 if:
    - Poll doesn't exist
    - Poll is inactive (soft-deleted)
    """
    poll = session.get(Poll, poll_id)
    
    if poll is None or not poll.is_active:
        raise HTTPException(
            status_code=404,
            detail="Poll not found"
        )
    
    return poll


@router.post("/{poll_id}/vote", response_model=Poll)
def vote_on_poll(
    poll_id: int,
    vote: VoteRequest,
    session: Session = Depends(get_session)
):
    """
    PUBLIC ENDPOINT: Cast a vote on an active poll.
    
    Increments either votes_a or votes_b based on the choice.
    Returns the updated poll with new vote counts.
    """
    poll = session.get(Poll, poll_id)
    
    # Verify poll exists and is active
    if poll is None or not poll.is_active:
        raise HTTPException(
            status_code=404,
            detail="Poll not found"
        )
    
    # Increment the appropriate vote counter
    if vote.choice == "a":
        poll.votes_a += 1
    else:
        poll.votes_b += 1
    
    # Save changes to database
    session.add(poll)
    session.commit()
    session.refresh(poll)
    
    return poll


# ==========================================
#  ADMIN ENDPOINTS (Protected by Token)
# ==========================================

@router.post(
    "/",
    response_model=Poll,
    status_code=201,
    dependencies=[Depends(verify_admin)]
)
def create_poll(
    poll_in: PollCreate,
    session: Session = Depends(get_session)
):
    """
    ADMIN ONLY: Create a new poll.
    
    Requires X-Admin-Token header.
    The poll is created as active by default.
    """
    poll = Poll.model_validate(poll_in)
    session.add(poll)
    session.commit()
    session.refresh(poll)
    return poll


@router.get(
    "/admin/list",
    response_model=list[Poll],
    dependencies=[Depends(verify_admin)]
)
def list_all_polls_admin(session: Session = Depends(get_session)):
    """
    ADMIN ONLY: List ALL polls (active and inactive).
    
    Requires X-Admin-Token header.
    Unlike the public endpoint, this shows soft-deleted polls too.
    Used by the admin UI to manage all polls.
    """
    statement = select(Poll)
    polls = session.exec(statement).all()
    return polls


@router.patch(
    "/{poll_id}/deactivate",
    response_model=Poll,
    dependencies=[Depends(verify_admin)]
)
def deactivate_poll(
    poll_id: int,
    session: Session = Depends(get_session)
):
    """
    ADMIN ONLY: Soft-delete a poll by marking it inactive.
    
    Requires X-Admin-Token header.
    
    Idempotent: If the poll is already inactive, returns immediately
    without making any database changes. This makes the endpoint safe
    to call multiple times (e.g., double-clicks, retries).
    
    Returns 404 if the poll doesn't exist.
    """
    poll = session.get(Poll, poll_id)
    
    if poll is None:
        raise HTTPException(
            status_code=404,
            detail="Poll not found"
        )
    
    # IDEMPOTENCY CHECK: Early return if already in desired state
    if not poll.is_active:
        return poll
    
    # Update state and save
    poll.is_active = False
    session.add(poll)
    session.commit()
    session.refresh(poll)
    
    return poll


@router.patch(
    "/{poll_id}/reactivate",
    response_model=Poll,
    dependencies=[Depends(verify_admin)]
)
def reactivate_poll(
    poll_id: int,
    session: Session = Depends(get_session)
):
    """
    ADMIN ONLY: Restore an inactive poll by marking it active.
    
    Requires X-Admin-Token header.
    
    Idempotent: If the poll is already active, returns immediately
    without making any database changes. This makes the endpoint safe
    to call multiple times (e.g., double-clicks, retries).
    
    Returns 404 if the poll doesn't exist.
    """
    poll = session.get(Poll, poll_id)
    
    if poll is None:
        raise HTTPException(
            status_code=404,
            detail="Poll not found"
        )
    
    # IDEMPOTENCY CHECK: Early return if already in desired state
    if poll.is_active:
        return poll
    
    # Update state and save
    poll.is_active = True
    session.add(poll)
    session.commit()
    session.refresh(poll)
    
    return poll