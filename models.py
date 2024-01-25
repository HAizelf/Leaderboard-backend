# models.py
from datetime import datetime
from pydantic import BaseModel
# models.py
from typing import Optional

class LeaderboardEntry(BaseModel):
    UID: Optional[str]
    Name: Optional[str]
    Score: Optional[int]
    Country: Optional[str]
    TimeStamp: Optional[str]


