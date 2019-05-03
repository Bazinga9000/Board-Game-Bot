from discord.ext import commands
import re as rgx
import discord
from io import TextIOWrapper, BytesIO
import sys, traceback
import subprocess
import asyncio
import concurrent

owner = lambda ctx: ctx.author.id == 137001076284063744
tracebackt = True

description = '''The Board Game Bot
Handles lots of things for Board Game TWOW
'''

# this specifies what extensions to load when the bot starts up
startup_extensions = ["admin"]

prefix = "bg!"

bot = commands.Bot(command_prefix=prefix, description=description)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@bot.event
async def on_ready():
    print()
    print(bcolors.OKGREEN + "Board Game Bot is Online!" + bcolors.ENDC)
    print(bcolors.OKBLUE + "User: " + bot.user.name + bcolors.ENDC)
    print(bcolors.OKBLUE + "ID: " + str(bot.user.id) + bcolors.ENDC)
    print(bcolors.OKBLUE + "Prefix: " + bot.command_prefix + bcolors.ENDC)



def gettraceback(exception):
    if not tracebackt: return
    lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
    print(''.join(lines))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        return await ctx.send("Uh oh! You friccin moron! You can't use this command in DMs!")
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You can't do that!")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        return await ctx.send(
            ctx.author.name + ", you need to put a handle on your stallions for {} more seconds. This command can only be used every {} sec!".format(
                round(error.retry_after, 2), error.cooldown.per))
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        e = str(error)
        arg = e.split(" ")[0]

        await ctx.send("Uh oh! You friccin moron! You forgot the `" + arg + "`!")
    elif isinstance(error, commands.UserInputError):
        e = ' '.join(error.args)
        error_data = rgx.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', e)
        if not error_data:
            print(bcolors.FAIL + "The command " + ctx.message.content)
            print("(Issued by " + ctx.author.name + " in " + gname + ")")
            print("caused " + str(error)[29:] + bcolors.ENDC)
            await ctx.send('Error: {}'.format(' '.join(error.args)))
            gettraceback(error)
        else:
            await ctx.send("Uh oh! You friccin moron! `{1}` isn't an `{0}`!".format(*error_data[0]))
    elif isinstance(error, commands.CommandInvokeError):
        o = error.original
        so = str(o)
        if isinstance(o, discord.HTTPException):
            if "Must be 2000 or fewer in length" in so:
                await ctx.send("Uh oh! You friccin moron! That message is too long!")
            elif "FORBIDDEN" in so:
                await ctx.send("Uh oh! I don't have permissions for this!")
        else:
            if ctx.guild is None:
                gname = " a DM"
            else:
                gname = ctx.guild.name
            print(bcolors.FAIL + "The command " + ctx.message.content)
            print("(Issued by " + ctx.author.name + " in " + gname + ")")
            print("caused " + str(error)[29:] + bcolors.ENDC)
            await ctx.send("Error: {}".format(' '.join(error.args)))
            gettraceback(error)
    else:
        print(bcolors.FAIL + "The command " + ctx.message.content)
        print("(Issued by " + ctx.author.name + " in " + gname + ")")
        print("caused " + str(error)[29:] + bcolors.ENDC)
        await ctx.send("Error: {}".format(' '.join(error.args)))
        gettraceback(error)


@bot.command()
@commands.check(owner)
async def toggletb(ctx):
    global tracebackt
    if tracebackt:
        tracebackt = False
        await ctx.send("Traceback has been turned off!")
    else:
        tracebackt = True
        await ctx.send("Traceback has been turned on!")


@bot.command()
@commands.check(owner)
async def load(ctx, extension_name: str):
    """Loads an extension."""

    try:
        bot.load_extension(extension_name)
        await ctx.send("{} loaded.".format(extension_name))
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return


@bot.command()
@commands.check(owner)
async def speak(ctx, channel: int, *, message: str):
    ch = bot.get_channel(channel)
    await ch.send(message)


@bot.command()
@commands.check(owner)
async def unload(ctx, extension_name: str):
    """Unloads an extension."""

    try:
        bot.unload_extension(extension_name)
        await ctx.send("{} unloaded.".format(extension_name))
    except:
        return


async def reload_libs(ctx):
    excount = len(startup_extensions)
    loaded = 0
    for extension in startup_extensions:
        try:
            bot.unload_extension(extension)
            bot.load_extension(extension)
            loaded += 1
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(bcolors.FAIL + 'Failed to load extension {}'.format(extension) + bcolors.ENDC + '\n{}'.format(exc))

    await ctx.send(str(loaded) + "/" + str(excount) + " Extensions Reloaded.")


#Stolen from HTBote
@bot.command(brief="Update the bot from git")
@commands.check(owner)
async def update(ctx):
    process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()


    stdout = stdout.decode().splitlines()
    stdout = '\n'.join('+ ' + i for i in stdout)
    stderr = stderr.decode().splitlines()
    stderr = '\n'.join('- ' + i for i in stderr)

    await ctx.author.send('`Git` response: ```diff\n{}\n{}```'.format(stdout, stderr))

    await reload_libs(ctx)


@bot.command(brief="Reload all the commands")
@commands.check(owner)
async def reload(ctx):
    await reload_libs(ctx)


'''
# Stolen from HTBote
@bot.command(brief="Update the bot from git")
@commands.check(owner)
async def update(ctx):
    process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    stdout = stdout.decode().splitlines()
    stdout = '\n'.join('+ ' + i for i in stdout)
    stderr = stderr.decode().splitlines()
    stderr = '\n'.join('- ' + i for i in stderr)

    await ctx.author.send('`Git` response: ```diff\n{}\n{}```'.format(stdout, stderr))

    await reload_libs(ctx)
'''

if __name__ == "__main__":

    bot.remove_command('help')

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print(bcolors.FAIL + 'Failed to load extension {}'.format(extension) + bcolors.ENDC + '\n{}'.format(exc))

with open("token.txt") as file:
    token = file.read().replace("\n", "")

bot.run(token)