from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db


# ||---------------------- Subject Model ----------------------||#
class Subject(db.Model):
    """Represents a subject area containing chapters and quizzes."""

    __tablename__ = "subjects"

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    chapters = relationship(
        "Chapter",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Subject {self.id}: {self.name}>"


# ||---------------------- Chapter Model ----------------------||#
class Chapter(db.Model):
    """Represents a chapter within a subject."""

    __tablename__ = "chapters"

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text, nullable=True)
    subject_id = db.Column(
        Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="chapters")
    quizzes = relationship(
        "Quiz", back_populates="chapter", cascade="all, delete-orphan", lazy=True
    )

    def __repr__(self):
        return f"<Chapter {self.id}: {self.name} (Subject ID: {self.subject_id})>"


# ||---------------------- Quiz Model ----------------------||#
class Quiz(db.Model):
    """Represents a quiz associated with a chapter."""

    __tablename__ = "quizzes"

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    title = db.Column(String(100), nullable=False)  # Changed from 'name'
    description = db.Column(Text, nullable=True)  # Changed from String(120)
    chapter_id = db.Column(
        Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    # Time duration in minutes
    time_duration = db.Column(Integer, nullable=True)
    remarks = db.Column(Text, nullable=True)  # Added remarks field
    created_at = db.Column(DateTime, default=datetime.utcnow)  # Replaces date_of_quiz
    is_published = db.Column(Boolean, default=False)  # Useful flag

    # Relationships
    chapter = relationship("Chapter", back_populates="quizzes")
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy=True,
    )
    attempts = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Quiz {self.id}: {self.title} (Chapter ID: {self.chapter_id})>"
