# Checks

## Custom checks
```python
from interactions import Client
from interactions.ext.checks import check

bot = Client(token="token")
bot.load("interactions.ext.checks")  # Needed!

def my_check(ctx):
    if ctx.author.id == bot.me.id:
        return True
    return False

@bot.command(name="check_example", description="Just an example command")
@check(my_check)
async def check_example(ctx):
    await ctx.send("Hello world!")

bot.start()
```

```python
from interactions import Client
from interactions.ext.checks import check, setup

bot = Client(token="token")
setup(bot)  # The alternative to `bot.load`

def my_check():
    def predicate(ctx):
        if ctx.author.id == bot.me.id:
            return True
        return False
    return check(predicate)

@bot.command(name="check_example", description="Just an example command")
@my_check()
async def check_example(ctx):
    await ctx.send("Hello world!")

bot.start()
```


## Pre-made checks
```python
from interactions import Client
from interactions.ext.checks import is_owner

bot = Client(token="token")
bot.load("interactions.ext.checks")

@bot.command(name="secrets", description="An owner only command")
@is_owner()
async def secrets(ctx):
    await ctx.send("Authorized eyes only")

bot.start()
```

## Multiple checks
```python
from interactions import Client
from interactions.ext.checks import is_owner, dm_only

bot = Client(token="token")
bot.load("interactions.ext.checks")

# Must pass both checks to succeed
@bot.command(name="secrets", description="An owner only command")
@is_owner()
@dm_only()
async def secrets(ctx):
    await ctx.send("Authorized eyes only")

bot.start()
```
