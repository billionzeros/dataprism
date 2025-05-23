import logging
import dspy
from app.utils import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)


class ChatModule(dspy.Module):
    """
    ChatModule is a class that represents a chat module in the application.
    It is responsible for handling chat-related operations and interactions.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._chat_id = None
        self._chat_service = None