from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.conversation import ConversationStatus
from app.models.message import SenderType

class MessageBase(BaseModel):
    content: str
    sender: SenderType

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    customer_id: int
    status: ConversationStatus

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageInDB] = []

    class Config:
        from_attributes = True

# Para listar conversaciones (sin mensajes)
class ConversationListItem(BaseModel):
    id: int
    customer_id: int
    customer_phone: Optional[str]
    status: ConversationStatus
    last_message: Optional[str]
    last_message_time: Optional[datetime]
    unread_count: int = 0  # podríamos implementarlo despuésfrom pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.conversation import ConversationStatus
from app.models.message import SenderType

class MessageBase(BaseModel):
    content: str
    sender: SenderType

class MessageCreate(MessageBase):
    pass

class MessageInDB(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    customer_id: int
    status: ConversationStatus

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageInDB] = []

    class Config:
        from_attributes = True

# Para listar conversaciones (sin mensajes)
class ConversationListItem(BaseModel):
    id: int
    customer_id: int
    customer_phone: Optional[str]
    status: ConversationStatus
    last_message: Optional[str]
    last_message_time: Optional[datetime]
    unread_count: int = 0  # podríamos implementarlo después