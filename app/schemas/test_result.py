from pydantic import BaseModel
from typing import List, Optional, Dict

class TestResult(BaseModel):
    results: List[Dict]
    result: Dict
    address: Optional[str] = None 