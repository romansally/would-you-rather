from sqlmodel import create_engine, SQLModel, Session

engine = create_engine("sqlite:///./polls.db", connect_args={"check_same_thread": False})

# create tables when app starts
def init_db():
    # Ensure models are registered with SQLModel's metadata before create_all
    from models import Poll
    SQLModel.metadata.create_all(engine) # looks at all models + builds the tables in database file
    
# add session maker (UPDATED TO FIX LEAK)
def get_session():
    with Session(engine) as session:
        yield session
    