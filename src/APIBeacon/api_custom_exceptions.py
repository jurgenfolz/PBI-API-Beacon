class APIError(Exception):
    """Base exception for all API related errors"""

class UnauthorizedError(Exception):
    """Raised when the user doesn't has access to the specified resource."""
    
class TokenExpiredError(Exception):
    """Raised when the token has expired."""

class TooManyRequestsError(Exception):
    """Too many requests sent in a short period of time."""

class InternalServerError(Exception):
    """Internal server error."""

class JSONDecodeError(APIError):
    """Raised when there's an issue decoding JSON from the response."""

class PowerBIEntityNotFoundError(Exception):
    """Exception raised when a Power BI entity is not found.

    Attributes:
        entity_name (str): name of the entity that was not found
        message (str): explanation of the error
    """

    def __init__(self, message="Entity not found."):
        self.message = message
        super().__init__(self.message)