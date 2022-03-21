# Cooldowns

## Cooldown on a single command
```python
from interactions import Client
from interactions.ext.checks import cooldown, Bucket

bot = Client(token="token")

@bot.command(name="bucket_example", description="Just an example command")
@cooldown(Bucket("guild_id", delay=15, count=3))
async def bucket_example(ctx):
    await ctx.send("Hello world!")

bot.start()
```

## Raise an error 
```python
from interactions import Client
from interactions.ext.checks import cooldown, Bucket, CommandOnCooldown

bot = Client(token="token")

@bot.command(name="error_example", description="Just an example command")
@cooldown(Bucket("guild_id", delay=15, count=3), error_on_fail=True)
async def error_example(ctx):
    await ctx.send("Hello world!")

# To be implemented by another ext
@error_example.error()
async def on_error(ctx, err):
    if isinstance(err, CommandOnCooldown):
        return await ctx.send(f"You have {err.remaining_time} left "
        "before you can use that command again")
    raise err

bot.start()
```


## Shared cooldown
```python
from interactions import Client
from interactions.ext.checks import cooldown, Bucket

bot = Client(token="token")

bucket = Bucket("guild_id", delay=15, count=3)

@bot.command(name="first_cooldown", description="The first of two commands")
@cooldown(bucket)
async def first_cooldown(ctx):
    await ctx.send("Lorem ipsum")

@bot.command(name="second_cooldown", description="The second of two commands")
@cooldown(bucket)
async def second_cooldown(ctx):
    await ctx.send("dolor sit amet")

bot.start()
```