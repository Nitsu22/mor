class MorphAppError(Exception):
    """Base exception for this application."""


class ValidationError(MorphAppError):
    """Raised when user input is invalid."""


class TagFormatError(MorphAppError):
    """Raised when a transcription tag cannot be expanded."""


class MecabError(MorphAppError):
    """Raised when MeCab cannot be used or returns invalid data."""
