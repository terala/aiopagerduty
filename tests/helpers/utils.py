"""Test helpers
"""
from typing import Optional, TypeVar, List, Callable

T = TypeVar("T")
TArg = TypeVar("TArg")
TResult = TypeVar("TResult")


def find_matching(arr: List[T], pred_fn: Callable[[T], bool]) -> Optional[T]:
    for x in arr:
        if pred_fn(x) is True:
            return x
    return None


def find_matching_or_throw(arr: List[T], pred_fn: Callable[[T], bool]) -> T:
    val: T | None = find_matching(arr, pred_fn)
    if val is None:
        raise LookupError()
    return val

