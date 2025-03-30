from sqlalchemy import (
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from extensions import db


class QuizAttempt(db.Model):
    """Stores the results and details of a user's quiz attempt."""

    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(
        db.Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    total_marks = db.Column(db.Integer, nullable=True)

    # Relationships
    student = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship(
        "Answer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self):
        return f"<QuizAttempt {self.id}: User {self.user_id} on Quiz {self.quiz_id} (Score: {self.score}/{self.total_marks})>"


class Answer(db.Model):
    """Stores a user's specific answer to a question in an attempt."""

    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attempt_id = db.Column(
        db.Integer,
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = db.Column(
        db.Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    selected_option_id = db.Column(
        db.Integer, ForeignKey("options.id", ondelete="SET NULL"), nullable=True
    )

    is_correct = db.Column(db.Boolean, nullable=True)
    points_awarded = db.Column(db.Integer, nullable=True, default=0)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question", backref="answers")
    selected_option = relationship("Option", foreign_keys=[selected_option_id])

    def __repr__(self):
        return f"<Answer {self.id}: Attempt {self.attempt_id}, Q {self.question_id}, Option {self.selected_option_id}>"
