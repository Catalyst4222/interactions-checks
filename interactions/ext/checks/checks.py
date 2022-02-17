import functools
from inspect import getfullargspec, isawaitable
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, Union

from interactions import Permissions

from . import errors

if TYPE_CHECKING:
    from interactions import CommandContext

    Check = Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    _T = TypeVar("_T")
    Coro = Callable[..., Awaitable[Any]]


def check(predicate: "Check") -> Callable[["Coro"], "Coro"]:
    """
    A decorator that only runs the wrapped function if the passed check returns True.

    Checks should only take a single argument, an instance of :class:`interactions.CommandContext`
    :param predicate: The check to run
    :type predicate: Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    """

    def decorator(
        coro: Callable[..., Awaitable["_T"]]
    ) -> Callable[..., Awaitable["_T"]]:

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


def is_owner() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the user is the owner of the bot

    :raise errors.NotOwner: The command user is not the bot owner
    """

    async def predicate(ctx):
        info = await ctx.client.http.get_current_bot_information()
        if int(ctx.author.user.id) == int(info["owner"]["id"]):
            return True
        raise errors.NotOwner

    return check(predicate)


def guild_only() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the command is ran in a guild

    :raise errors.NoDMs: The command was ran in a DM
    """

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is None:
            raise errors.NoDMs
        return True

    return check(predicate)


def dm_only() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the command is ran outside a guild

    :raise errors.DMsOnly: The command was ran outside of a DM
    """

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is not None:
            raise errors.DMsOnly
        return True

    return check(predicate)


def has_permissions(**perms: bool) -> Callable[["Coro"], "Coro"]:
    def predicate(ctx: "CommandContext") -> bool:
        for perm, value in perms.items():
            if (Permissions[perm.upper()] in ctx.author.permissions) is not value:
                return False

        raise errors.MissingPermissions  # todo add the missing perms in the raise

    return check(predicate)


def is_admin(guild_only: bool = True) -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the user is an administrator

    :param bool guild_only: If the command should fail if in a dm
    :raise errors.NoDMs: The command was ran in a DM
    :raise errors.NotAdmin: The command was ran by a standard user
    """

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is None:
            if guild_only:
                raise errors.NoDMs
            return True

        if int(ctx.author.permissions) & 8:  # 8 is the administrator permission
            return True
        raise errors.NotAdmin

    return check(predicate)
