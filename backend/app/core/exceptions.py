"""Shared application-level exception classes."""


class AppError(RuntimeError):
    """Base class for expected application-level errors."""


class DatabaseOperationError(AppError):
    """Raised when a database query or persistence operation fails."""


class LLMServiceError(AppError):
    """Raised when an upstream LLM call cannot be completed safely."""


class PromptManagerError(AppError):
    """Raised when a required prompt resource cannot be loaded."""


class StructuredOutputError(AppError):
    """Raised when structured LLM output cannot be parsed or normalized."""


class UnsupportedTargetLanguageError(AppError):
    """Raised when a feature does not support the requested target language."""
