from asyncio import Semaphore
from typing import TYPE_CHECKING, List

from interactions import CommandContext

if TYPE_CHECKING:
    from . import Bucket


class CheckFailure(Exception):
    """Generic error to be raised when a check failed"""

    msg = "A generic check failed"

    def __init__(self, ctx: CommandContext, message: str = None, *args):
        super().__init__(message or self.msg.format(ctx), *args)
        self.ctx = ctx


class NotOwner(CheckFailure):
    """Raised by :func:`checks.is_owner` when the user isn't the bot owner"""

    msg = "You are not the owner"


class NoDMs(CheckFailure):
    """Raised by :func:`checks.guild_only` when a command is ran in dms"""

    msg = "This command can't be ran in dms"


class DMsOnly(CheckFailure):
    """Raised by :func:`checks.dm_only` when a command isn't ran in dms"""

    msg = "This command can't be ran outside dms"


class MissingPermissions(CheckFailure):
    """Raised by :func:`checks.has_permissions` when the user doesn't have the required permissions"""

    msg = "You do not have the proper permissions"

    def __init__(self, ctx: CommandContext, missing_permissions: List[str], *args) -> None:
        self.missing_permissions: List[str] = missing_permissions

        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in missing_permissions
        ]

        if len(missing) > 2:
            fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = " and ".join(missing)
        message = f"You are missing {fmt} permission(s) to run this command."

        super().__init__(ctx, message, *args)

        self.msg = message


class NotAdmin(CheckFailure):
    """Raised by :func:`checks.has_permissions` when the user is not an administrator"""

    msg = "You are not an administrator"


class CommandOnCooldown(CheckFailure):
    """Raised by :func:`cooldown.cooldown` when the command isn't ready to be used"""

    msg = "This command is on cooldown"

    def __init__(self, ctx: CommandContext, bucket: "Bucket", *args):
        message = f"This command will get off cooldown in {bucket.remaining_time(ctx)} seconds"
        super().__init__(ctx, message, *args)
        self.bucket = bucket
        self.remaining_time = bucket.remaining_time()


class MaxConcurrencyReached(CheckFailure):
    """raised by :func:`concurrency.limit_concurrency` when too many instances of a command are being ran"""

    msg = "This command has too many instances running"

    def __init__(self, ctx: CommandContext, sem: Semaphore, *args):
        message = f"This command already has {sem._value} instances running"
        super().__init__(ctx, message, *args)
