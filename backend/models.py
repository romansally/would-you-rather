# models.py
# Defines the database schema and API data model for Poll objects.
# SQLModel is used here because it combines SQLAlchemy (database ORM) 
# and Pydantic (data validation / JSON serialization).
from typing import Optional
from sqlmodel import SQLModel, Field

class Poll(SQLModel, table=True):
    """
    Poll represents a single 'Would You Rather' style question.
    Each row in the database corresponds to one poll with two possible options.
    """
    
    # Primary key: unique identifier for each poll.
    # Optional at creation time (None) because the database auto-generates it.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Category of the poll (e.g., "movies", "food", "sports").
    # Defaults to "general" if none is specified.
    category: str = "general" # poll category (movies, food, sports, etc.)
    question: str # poll question text
    option_a: str # first choice/option
    option_b: str # second choice/option
    votes_a: int = 0 # count of option A 
    votes_b: int = 0 # count of option B
    is_active: bool = True # soft delete flag
