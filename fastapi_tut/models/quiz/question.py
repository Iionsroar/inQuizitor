from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List
from fastapi_tut.db.base_class import PKModel
from fastapi_tut.models.quiz.quiz import Quiz


class QuizQuestionBase(SQLModel):
    content: str = Field(max_length=200)
    points : int
    order : int
    quiz_id : Optional[int] = Field(default=None, foreign_key="quiz.id")

class QuizQuestionCreate(QuizQuestionBase):
    pass

class QuizQuestionUpdate(QuizQuestionBase):
    content: Optional[str] = None
    points : Optional[int] = None
    order : Optional[int] = None

class QuizQuestionInDBBase(QuizQuestionBase, PKModel):
    pass

class QuizQuestion(QuizQuestionInDBBase, table=True):
    choices: List["QuizChoice"] = Relationship(back_populates="question")
    attempts: List["QuizAttempt"] = Relationship(back_populates="question")
    quiz: Optional[Quiz] = Relationship(back_populates="questions")
    
    def __repr__(self):
        return f"<Question({self.content!r})>"
    
class QuizQuestionRead(QuizQuestionBase):
    id: int
    quiz_id: int

class QuizQuestionReadWithChoices(QuizQuestionBase):

    choices: List["QuizChoice"] = []

from fastapi_tut.models.quiz.choice import QuizChoice
QuizQuestionReadWithChoices.update_forward_refs()