from pydantic import BaseModel

class TextualQuestion(BaseModel):
    text: str

class SolutionResponse(BaseModel):
    result: str
    details: dict = None 