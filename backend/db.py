from sqlmodel import create_engine, SQLModel, Session

engine = create_engine("sqlite:///./polls.db", connect_args={"check_same_thread": False})
