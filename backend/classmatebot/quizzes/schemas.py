from typing import List, Dict

from pydantic import BaseModel, Field


class QuizSchema(BaseModel):
    questions: Dict[str, List[str]] = Field(description='Dictionary of questions and their list of options. The key is question and the value is a '
                                                        'List of options')