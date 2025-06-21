from pydantic import BaseModel
from typing import List

class TestResultResponse(BaseModel):
    store: str
    description: str
    category: str
    keywords: List[str]
    logo_url: str

class TestResult(BaseModel):
    result: TestResultResponse
    address: str 