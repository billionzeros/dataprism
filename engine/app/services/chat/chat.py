import uuid
import logging
import datetime
from typing import Dict
from app.utils import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)

# Active Chats Maps
active_chats_maps: Dict[str, str] = {}

class ChatService:
    """
    ChatService is a class that provides methods to interact with the chat service.
    """
    def __init__(self, chat_id: uuid.UUID):
        """
        chat_id (uuid.UUID): The unique identifier for the chat session.
        """
        self._chat_id: uuid.UUID = chat_id
        """
        chat_id (uuid.UUID): The unique identifier for the chat session.
        """

        self._created_at = datetime.datetime.now()
        """
        created_at (datetime): The timestamp when the chat session was created.
        """

    @property
    def chat_id(self) -> uuid.UUID:
        """
        Get the chat ID
        """
        return self._chat_id

    @classmethod
    def get_chat(cls, chat_id: str) -> "ChatService":
        """
        Static Function to Get a chat session by ID

        Args:
            chat_id (str): The ID of the chat session to retrieve.

        Returns:
            ChatService: An instance of the ChatService class with the specified chat ID.

        Raises:
            ValueError: If the chat ID is not found in the active chats maps.
        """
        if chat_id not in active_chats_maps:
            raise ValueError(f"Chat ID {chat_id} not found")

        return cls(chat_id=uuid.UUID(chat_id))
    
    @classmethod
    def create(cls) -> "ChatService":
        """
        Static Function to Create a new chat session and return the ChatService instance
        """
        chat_uid: uuid.UUID = uuid.uuid4()

        chat_service =  cls(chat_id=chat_uid)  
        
        active_chats_maps[str(chat_uid)] = str(chat_service.chat_id)

        return chat_service  