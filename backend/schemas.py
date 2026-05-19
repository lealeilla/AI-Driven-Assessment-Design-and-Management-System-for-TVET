from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# ── Auth ──────────────────────────────────────────────────────────────
class TeacherCreate(BaseModel):
    name    : str
    email   : str
    password: str
    school  : str

class TeacherLogin(BaseModel):
    email   : str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type  : str = "bearer"
    teacher_name: str

# ── Exam generation ───────────────────────────────────────────────────
class ExamRequest(BaseModel):
    program         : str
    level           : int
    module          : str
    learning_outcome: str        # "all" or specific outcome
    num_questions   : int
    total_marks     : int
    exam_date       : str
    time_allowed    : str

class QuestionOut(BaseModel):
    number          : int
    learning_outcome: str
    bloom_level     : str
    question_type   : str
    question        : str
    options         : Any
    correct_answer  : Optional[str]
    marks           : int
    topic           : str

    class Config:
        from_attributes = True

class ExamOut(BaseModel):
    exam_id         : int
    program         : str
    level           : int
    module          : str
    assessment_type : str
    total_marks     : int
    num_questions   : int
    questions       : List[QuestionOut]

# ── Question bank ─────────────────────────────────────────────────────
class QuestionBankItem(BaseModel):
    id              : int
    program         : str
    level           : int
    module          : str
    learning_outcome: str
    bloom_level     : str
    question_type   : str
    question        : str
    options         : Any
    correct_answer  : Optional[str]
    marks           : int
    topic           : str
    times_used      : int

    class Config:
        from_attributes = True

# ── Modules ───────────────────────────────────────────────────────────
class ModuleInfo(BaseModel):
    program : str
    level   : int
    module  : str
    outcomes: List[str]