from typing import Type

import interactions
from interactions import CommandContext

from .attribute import Attribute
from .errors import CheckFailure

__all__ = ("setup",)


def _command_patch(Command: Type[interactions.Command]):
    old_init = Command.__init__
    old_dispather: property = Command.__dict__["dispatcher"]

    def new_command_init(self: interactions.Command, *args, **kwargs):
        old_init(self, *args, **kwargs)  # noqa
        self.__command_checks__ = getattr(self.coro, "__command_checks__", [])

    def dispatch_wrapper(self: Command):
        async def new_command_dispatcher(ctx: CommandContext, *args, **kwargs):
            checks = self.__command_checks__
            ctx.channel.history()

            # look through the check too see if they all pass
            try:
                for check in checks:
                    if not await check(ctx):
                        raise CheckFailure(ctx)
                return await old_dispather.__get__(self, Command)(
                    ctx, *args, **kwargs
                )  # Property shenanigans
            except CheckFailure as e:
                error = e

            # handle the exception
            if not (self.error_callback or self.listener):
                raise error

            if self.error_callback:
                if self.extension:
                    self.error_callback(self.extension, ctx, error)
                else:
                    self.error_callback(ctx, error)

            if self.listener:
                self.listener.dispatch("on_command_error", ctx, error)

        return new_command_dispatcher

    Command.__command_checks__ = Attribute()
    Command.__init__ = new_command_init
    setattr(
        Command,
        "dispatcher",
        property(
            dispatch_wrapper,
            old_dispather.fset,
            old_dispather.fdel,
            old_dispather.__doc__,
        ),
    )

    # todo add the check manager functions


def setup(bot):
    import interactions

    print("setup")
    _command_patch(interactions.Command)
