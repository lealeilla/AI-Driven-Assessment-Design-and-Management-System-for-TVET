from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:lea123@localhost:5432/tvet_db")

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()

# ── MODELS ────────────────────────────────────────────────────────────
class Teacher(Base):
    __tablename__ = "teachers"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100))
    email      = Column(String(100), unique=True, index=True)
    password   = Column(String(200))
    school     = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    exams      = relationship("Exam", back_populates="teacher")


class Exam(Base):
    __tablename__ = "exams"
    id              = Column(Integer, primary_key=True, index=True)
    teacher_id      = Column(Integer, ForeignKey("teachers.id"))
    program         = Column(String(100))
    level           = Column(Integer)
    module          = Column(String(200))
    learning_outcome= Column(String(300))
    assessment_type = Column(String(20))   # Formative / Summative
    num_questions   = Column(Integer)
    total_marks     = Column(Integer)
    exam_date       = Column(String(50))
    time_allowed    = Column(String(50))
    created_at      = Column(DateTime, default=datetime.utcnow)
    teacher         = relationship("Teacher", back_populates="exams")
    questions       = relationship("Question", back_populates="exam")


class Question(Base):
    __tablename__ = "questions"
    id              = Column(Integer, primary_key=True, index=True)
    exam_id         = Column(Integer, ForeignKey("exams.id"))
    number          = Column(Integer)
    learning_outcome= Column(String(300))
    bloom_level     = Column(String(20))
    question_type   = Column(String(20))
    question        = Column(Text)
    options         = Column(JSON)
    correct_answer  = Column(Text)
    marks           = Column(Integer)
    topic           = Column(String(200))
    exam            = relationship("Exam", back_populates="questions")


class QuestionBank(Base):
    __tablename__ = "question_bank"
    id              = Column(Integer, primary_key=True, index=True)
    program         = Column(String(100))
    level           = Column(Integer)
    module          = Column(String(200))
    learning_outcome= Column(String(300))
    bloom_level     = Column(String(20))
    question_type   = Column(String(20))
    question        = Column(Text)
    options         = Column(JSON)
    correct_answer  = Column(Text)
    marks           = Column(Integer)
    topic           = Column(String(200))
    times_used      = Column(Integer, default=0)
    created_at      = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created!")