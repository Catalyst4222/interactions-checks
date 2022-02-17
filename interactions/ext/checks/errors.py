# TODO super().__init__ w/ default error messages


class CheckFailure(Exception):
    """Generic error to be raised when a check failed"""


class NotOwner(CheckFailure):
    """Raised by :func:`checks.is_owner` when the user isn't the bot owner"""


class NoDMs(CheckFailure):
    """Raised by :func:`checks.guild_only` when a command is ran in dms"""


class DMsOnly(CheckFailure):
    """Raised by :func:`checks.dm_only` when a command isn't ran in dms"""


class MissingPermissions(CheckFailure):
    """Raised by :func:`checks.has_permissions` when the user doesn't have the required permissions"""

    def __init__(self, missing_permissions: list[str], *args) -> None:
        self.missing_permissions: list[str] = missing_permissions

        missing = [
            perm.replace("_", " ").replace("guild", "server").title()
            for perm in missing_permissions
        ]

        if len(missing) > 2:
            fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = " and ".join(missing)
        message = f"You are missing {fmt} permission(s) to run this command."
        super().__init__(message, *args)


class NotAdmin(CheckFailure):
    """Raised by :func:`checks.has_permissions` when the user is not an administrator"""


class CommandOnCooldown(CheckFailure):
    """Raised by :func:`cooldown.cooldown` when the command isn't ready to be used"""

    # todo remaining time
