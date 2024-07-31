import aiohttp


class DuckChatException(aiohttp.client.ClientError):
    """Base exception class for duck_chat."""


class RatelimitException(DuckChatException):
    """Raised for rate limit exceeded errors during API requests."""


class ConversationLimitException(DuckChatException):
    """Raised for conversation limit during API requests to AI endpoint."""
