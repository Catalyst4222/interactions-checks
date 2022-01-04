import functools
from inspect import isawaitable, getfullargspec
from typing import Union, Callable, Coroutine

from . import errors


def check(predicate: Union[Callable, Coroutine]) -> Callable:
    def decorator(coro: Callable[..., Coroutine]):

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
