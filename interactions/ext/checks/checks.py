import asyncio
import functools
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, Union

from interactions import Command, CommandContext, Permissions, Role, Snowflake

from . import errors

if TYPE_CHECKING:
    Check = Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    _T = TypeVar("_T")
    Coro = Callable[..., Awaitable[Any]]
    CoroOrCommand = TypeVar("CoroOrCommand", Coro, Command)

__all__ = (
    "check",
    "old_style_check",
    "is_owner",
    "guild_only",
    "dm_only",
    "has_permissions",
    "is_admin",
    "has_role",
)


def check(predicate: "Check") -> Callable[["_T"], "_T"]:
    """
    A decorator that only runs the wrapped function if the passed check returns True.

    Checks should only take a single argument, an instance of :class:`interactions.CommandContext`
    :param predicate: The check to run
    :type predicate: Callable[[CommandContext], Union[bool, Awaitable[bool]]]
    """

    if not asyncio.iscoroutinefunction(predicate):
        # Wrap in a coroutine
        async def _predicate(*args, **kwargs):
            return predicate(*args, **kwargs)

    else:
        _predicate = predicate

    def decorator(coro_or_command: "CoroOrCommand") -> "CoroOrCommand":
        if getattr(coro_or_command, "__command_checks__", None) is None:
            coro_or_command.__command_checks__ = []
        checks = coro_or_command.__command_checks__
        checks.append(_predicate)
        return coro_or_command

    return decorator


def old_style_check(predicate: "Check") -> Callable[["_T"], "_T"]:
    def decorator_(coro: Callable[..., Awaitable["_T"]]) -> Callable[..., Awaitable["_T"]]:

        if "." in coro.__qualname__:  # To future proof classes

            @functools.wraps(coro)
            async def inner(self, ctx, *args, **kwargs):
                res = predicate(ctx)
                if isawaitable(res):
                    res = await res

                if not res:
                    raise errors.CheckFailure(ctx)

                return await coro(self, ctx, *args, **kwargs)

        else:

            @functools.wraps(coro)
            async def inner(ctx, *args, **kwargs):
                res = predicate(ctx)
                if isawaitable(res):
                    res = await res

                if not res:
                    raise errors.CheckFailure(ctx)

                return await coro(ctx, *args, **kwargs)

        return inner

    return decorator_


def is_owner() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the user is the owner of the bot

    :raise errors.NotOwner: The command user is not the bot owner
    """

    async def predicate(ctx: "CommandContext"):
        info = await ctx.client.get_current_bot_information()
        if int(ctx.author.user.id) == int(info["owner"]["id"]):
            return True
        raise errors.NotOwner(ctx)

    return check(predicate)


def guild_only() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the command is ran in a guild

    :raise errors.NoDMs: The command was ran in a DM
    """

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is None:
            raise errors.NoDMs(ctx)
        return True

    return check(predicate)


def dm_only() -> Callable[["Coro"], "Coro"]:
    """
    A check that only succeeds when the command is ran outside a guild

    :raise errors.DMsOnly: The command was ran outside of a DM
    """

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is not None:
            raise errors.DMsOnly(ctx)
        return True

    return check(predicate)


def has_permissions(**perms: bool) -> Callable[["Coro"], "Coro"]:
    def predicate(ctx: "CommandContext") -> bool:  # todo add overrides
        if missing_perms := [
            *filter(
                lambda perm: (Permissions[perm.upper()] in ctx.author.permissions)
                is not perms[perm],
                perms,
            )
        ]:
            raise errors.MissingPermissions(ctx, missing_perms)

        return True

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
                raise errors.NoDMs(ctx)
            return True

        if int(ctx.author.permissions) & 8:  # 8 is the administrator permission
            return True
        raise errors.NotAdmin(ctx)

    return check(predicate)


def has_role(
    *roles: Union[str, int, Snowflake],
    require_all: bool = False,
    guild_only: bool = True,
) -> Callable[["Coro"], "Coro"]:
    """
    A check that makes sure the author has the right role names/ids

    :param Union[str, int] roles: The role names or ids
    :param bool require_all: If the user needs every role or just one, defaults to just one
    :param bool guild_only: If the command should fail if in a dm
    :raise errors.NoDMs: The command was ran in a DM
    :raise errors.MissingRole: The author does not have the needed roles
    """

    def _has_role(author_role: Union["Role", int]) -> bool:
        if isinstance(author_role, Role):
            return author_role.name in roles or author_role.id in roles
        return author_role in roles

    def predicate(ctx: "CommandContext"):
        if ctx.guild_id is None:
            if guild_only:
                raise errors.NoDMs(ctx)
            return True

        if require_all:
            return all(_has_role(role) for role in ctx.author.roles)
        return any(_has_role(role) for role in ctx.author.roles)

    return check(predicate)
