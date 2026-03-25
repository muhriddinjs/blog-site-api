from pydantic import BaseModel
from typing import List

class StatItem(BaseModel):
    value: str
    label: str

class AboutBase(BaseModel):
    name: str
    title: str
    tagline: str
    bio: str
    stats: List[StatItem] = []

class AboutCreate(AboutBase):
    pass

class AboutUpdate(AboutBase):
    pass

class AboutResponse(AboutBase):
    id: int

    class Config:
        from_attributes = True
