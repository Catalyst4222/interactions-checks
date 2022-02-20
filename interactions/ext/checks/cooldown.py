import time
from functools import wraps
from typing import Dict, List

from interactions import CommandContext

from . import errors


class Bucket:
    """
    A class designed for controlling cooldowns on functions
    """

    def __init__(self, attribute: str, delay: int, count: int):
        """
        :param attribute: The attribute of ctx to check, e.g. guild
        :type attribute: str
        :param delay: How long to wait before resetting the cooldown
        :type delay: int
        :param count: How many times the command be used before needing to be cooled down
        :type count: int
        """
        self.attribute: str = attribute
        self.cooldown: int = delay
        self.count: int = count

        self._timers: Dict[..., List[float]] = {}  # todo test with defaultdict

    def _clean_timers(self):
        """Clean out any outdated times"""
        for times in self._timers.values():
            for timer in times:
                if timer + self.cooldown < time.time():
                    times.remove(timer)

    def _get_times(self, ctx) -> list[float]:
        """Get the"""
        key = getattr(ctx, self.attribute)
        if hasattr(key, "id"):
            key = key.id
        try:
            key = int(key)
        except TypeError:
            pass

        timers = self._timers.get(key)
        if timers is None:
            timers = []
            self._timers[key] = timers
        return timers

    def can_run(self, ctx: "CommandContext") -> bool:
        """
        A method to determine if the command is off cooldown
        :param ctx: The context of the command
        :type ctx: Context
        :return: If the command can run
        :rtype: bool
        """
        self._clean_timers()

        timers = self._get_times(ctx)

        if len(timers) >= self.count:
            return False

        timers.append(time.time())

        return True

    def remaining_time(self, ctx: "CommandContext") -> float:
        self._clean_timers()

        times = self._get_times(ctx)

        if len(times) < self.count:
            return 0.0

        return (min(times) + self.cooldown) - time.time()


def cooldown(bucket: Bucket, error_on_fail: bool = False):
    def inner(func):
        @wraps(func)
        async def new_func(ctx: "CommandContext", *args, **kwargs):
            # todo cooldown logic
            if bucket.can_run(ctx):
                return await func(ctx, *args, **kwargs)

            if error_on_fail:
                raise errors.CommandOnCooldown(ctx, bucket)

            await ctx.send(
                f"This command will get off cooldown in {bucket.remaining_time(ctx):2f} seconds"
            )

        # Change over special data
        new_data = filter(lambda attr: attr not in dir(type(func)), dir(func))
        for new_attr in new_data:
            old_attr = getattr(func, new_attr)
            setattr(new_func, new_attr, old_attr)

        return new_func

    return inner
