from functools import wraps
from fastapi import HTTPException
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

def handle_exceptions(status_code: int = 500) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    A decorator that handles both HTTPException and general exceptions.
    
    Args:
        status_code: The status code to use for non-HTTP exceptions
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise  # Re-raise HTTP exceptions as-is
            except Exception as e:
                raise HTTPException(status_code=status_code, detail=str(e))
        return wrapper
    return decorator 