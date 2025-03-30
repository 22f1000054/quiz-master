from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from extensions import db


class Question(db.Model):
    """Represents a question within a quiz."""

    __tablename__ = "questions"

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )

    question_text = db.Column(Text, nullable=False)
    points = db.Column(Integer, default=1, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:50]}... (Quiz ID: {self.quiz_id})>"


class Option(db.Model):
    """Represents a possible answer option for a question."""

    __tablename__ = "options"

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    option_text = db.Column(Text, nullable=False)
    is_correct = db.Column(Boolean, default=False, nullable=False)

    question = relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<Option {self.id}: {self.option_text[:50]}... (Correct: {self.is_correct})>"
