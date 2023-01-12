class APIError(Exception):
    """All custom API Exceptions"""
    pass


class APIAuthError(APIError):
    """Custom Authentication Error Class."""
    def __init__(self, message, code=401):
        self.code = code
        self.message = message
        super().__init__(self.message)


class APINotFoundError(APIError):
    """Custom Not Found Item Error Class."""
    def __init__(self, message, code=404):
        self.code = code
        self.message = message
        super().__init__(self.message)


class APIUnknownKeyError(APIError):
    """Custom Unknown Key Error Class."""
    def __init__(self, message, code=400):
        self.code = code
        self.message = message
        super().__init__(self.message)


class APITokenError(APIError):
    """Custom Token Error Class."""
    def __init__(self, message, code=403):
        self.code = code
        self.message = message
        super().__init__(self.message)
