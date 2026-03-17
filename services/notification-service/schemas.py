from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: int
    type: str = Field(..., regex="^(email|sms|push)$")
    subject: Optional[str] = None
    content: str
    recipient: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    subject: Optional[str]
    content: str
    recipient: str
    status: str
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailTemplate(BaseModel):
    subject: str
    body: str
    html_body: Optional[str] = None

class NotificationTemplateCreate(BaseModel):
    name: str
    type: str = Field(..., regex="^(email|sms|push)$")
    subject: Optional[str] = None
    body: str
    html_body: Optional[str] = None
    is_active: bool = True

class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    type: str
    subject: Optional[str]
    body: str
    html_body: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
