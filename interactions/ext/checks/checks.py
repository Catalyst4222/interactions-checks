import functools
from inspect import isawaitable, getfullargspec
from typing import Union, Callable, Coroutine, Awaitable, TypeVar, Any, TYPE_CHECKING

from . import errors

if TYPE_CHECKING:
    from interactions import CommandContext

    Check = Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    _T = TypeVar("_T")
    Coro = Callable[..., Coroutine[Any]]


def check(predicate: "Check") -> Callable[["Coro"], "Coro"]:
    """
    A decorator that only runs the wrapped function if the passed check returns True.

    Checks should only take a single argument, an instance of :class:`interactions.CommandContext`
    :param predicate: The check to run
    :type predicate: Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    """

    def decorator(coro: Callable[..., Coroutine[_T]]) -> Callable[..., Coroutine[_T]]:

        if getfullargspec(coro).args[0] == "self":  # To future proof classes

            @functools.wraps(coro)
            async def inner(self, ctx, *args, **kwargs):
                res = predicate(ctx)
                if isawaitable(res):
                    res = await res

                if not res:
                    raise errors.CheckFailure

                return await coro(self, ctx, *args, **kwargs)

        else:

            @functools.wraps(coro)
            async def inner(ctx, *args, **kwargs):
                res = predicate(ctx)
                if isawaitable(res):
                    res = await res

                if not res:
                    raise errors.CheckFailure

                return await coro(ctx, *args, **kwargs)

        return inner

    return decorator
