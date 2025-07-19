"""
ChainableWrapper Exceptions Module
================================
This module defines custom exceptions for the ChainableWrapper class, providing specific error handling for type,
value, key, index, and general exceptions. Each exception logs an error message when raised.
"""

import logging

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class ChainableWrapperError(Exception):
    """
    Exceção personalizada para erros específicos do ChainableWrapper.
    Pode ser estendida para casos de erro mais específicos no futuro.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperError: %s", self.message)


class ChainableWrapperTypeError(ChainableWrapperError, TypeError):
    """
    Exceção personalizada para erros de tipo no ChainableWrapper.
    Herda de ChainableWrapperError e TypeError para manter a hierarquia de exceções.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperTypeError: %s", self.message)

    def __str__(self) -> str:
        return f"ChainableWrapperTypeError: {self.message}"


class ChainableWrapperValueError(ChainableWrapperError, ValueError):
    """
    Exceção personalizada para erros de valor no ChainableWrapper.
    Herda de ChainableWrapperError e ValueError para manter a hierarquia de exceções.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperValueError: %s", self.message)

    def __str__(self) -> str:
        return f"ChainableWrapperValueError: {self.message}"


class ChainableWrapperKeyError(ChainableWrapperError, KeyError):
    """
    Exceção personalizada para erros de chave no ChainableWrapper.
    Herda de ChainableWrapperError e KeyError para manter a hierarquia de exceções.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperKeyError: %s", self.message)

    def __str__(self) -> str:
        return f"ChainableWrapperKeyError: {self.message}"


class ChainableWrapperIndexError(ChainableWrapperError, IndexError):
    """
    Exceção personalizada para erros de índice no ChainableWrapper.
    Herda de ChainableWrapperError e IndexError para manter a hierarquia de exceções.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperIndexError: %s", self.message)

    def __str__(self) -> str:
        return f"ChainableWrapperIndexError: {self.message}"


class ChainableWrapperException(ChainableWrapperError):
    """
    Exceção genérica para erros no ChainableWrapper.
    Pode ser usada para capturar erros que não se encaixam nas categorias específicas.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        logger.error("ChainableWrapperException: %s", self.message)

    def __str__(self) -> str:
        return f"ChainableWrapperException: {self.message}"
