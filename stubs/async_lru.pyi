"""Type hints for async_lru module"""

from typing import Any, Callable


# pylint: disable=unused-argument
def alru_cache(fn: Callable[..., Any] | None = ..., maxsize: int = ...,
               typed: bool = ..., *, cache_exceptions: bool = ...) -> Callable[..., Any]: ...
