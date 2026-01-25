from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class ProjectRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    project_type = Column(String)
    description = Column(Text)
    budget = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
