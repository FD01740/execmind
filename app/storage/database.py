import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DATABASE_URL = "sqlite:///execmind.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    raw_input = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    target_users = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    source = Column(String, default="text") # 'text' or 'voice'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="idea")

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    feasibility = Column(Integer)
    market_value = Column(Integer)
    complexity = Column(Integer)
    risk = Column(Integer)
    innovation = Column(Integer)
    final_score = Column(Float)
    verdict = Column(String) # 'pursue', 'refine', 'drop'
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    idea = relationship("Idea", back_populates="evaluations")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
