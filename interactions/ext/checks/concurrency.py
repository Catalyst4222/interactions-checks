from asyncio import Semaphore
from functools import wraps
from typing import Literal

from . import errors

__all__ = ("limit_concurrency",)


def limit_concurrency(
    amount: int,
    wait: bool = True,
    defer: Literal[True, False, "ephemeral"] = True,
    error_on_fail: bool = False,
):  # todo limit by bucket?

    sem = Semaphore(amount)

    def inner(func):
        @wraps(func)
        async def concurrency_func(ctx, *args, **kwargs):
            if defer and wait:
                await ctx.defer(ephemeral=defer == "ephemeral")

            if not wait and sem.locked():
                if error_on_fail:
                    raise errors.MaxConcurrencyReached(ctx, sem)

                await ctx.send("This command has reached the concurrency limit")
                return
            async with sem:
                return await func(ctx, *args, **kwargs)

        return concurrency_func

    return inner
