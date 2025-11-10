from typing import List, Dict

from pydantic import BaseModel, Field


class TopicSchema(BaseModel):
    bites: List[str] = Field(description="List of bites in a Topic")
    

class PreferencesSchema(BaseModel):
    preferences: str = Field(description="User preferences for generating topic content")    
    topic_content: str = Field(description="Generated topic content based on user preferences")
    topic_name: str = Field(description="Generated topic name based on user preferences")
    topic_description: str = Field(description="Generated topic description based on user preferences")
    subject_name: str = Field(description="Generated subject name based on user preferences")
    subject_description: str = Field(description="Generated subject description based on user preferences")