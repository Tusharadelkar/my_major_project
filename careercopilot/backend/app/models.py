from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    job_description = Column(Text, nullable=False)
    ats_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="sessions")
    qa_records = relationship("QARecord", back_populates="session", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="session", cascade="all, delete-orphan")


class QARecord(Base):
    __tablename__ = "qa_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer_transcript = Column(Text, nullable=True)
    technical_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    skill_tag = Column(String(100), nullable=True)
    audio_path = Column(String(500), nullable=True)
    audio_base64 = Column(Text, nullable=True)  # Cached TTS audio to avoid regeneration on every load
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="qa_records")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # e.g., "identified", "resolved"

    # Relationships
    session = relationship("Session", back_populates="skill_gaps")
