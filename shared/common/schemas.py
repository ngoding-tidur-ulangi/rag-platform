from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class DefaultResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    code: int = 200

    @classmethod
    def success(cls, data: Any = None, message: str = "Ok", code: int = 200):
        return cls(message=message, data=data, code=code)

    @classmethod
    def error(cls, message: str = "Internal Server Error", code: int = 500, data: Any = None):
        return cls(message=message, data=data, code=code)
