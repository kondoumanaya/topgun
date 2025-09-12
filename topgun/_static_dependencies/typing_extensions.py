"""
Compatibility layer for typing_extensions
Python 3.12+ optimized version for development environment
"""
from typing import (
    Final, Literal, get_origin, get_args, Annotated, dataclass_transform
)

__all__ = ['get_origin', 'get_args', 'Annotated', 'dataclass_transform', 'Final', 'Literal']