import discord
from discord.ext import commands
import sys, io, json

owner = lambda ctx: ctx.author.id in [137001076284063744,223201675186274304,473975633014161419]

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(489554436327211008)

    def get_name(self, id):
        return self.guild.get_member(id).name

    def get_results(self):
        x = self.bot.game.export_results()
        for response in x:
            response["name"] = self.get_name(response["player"])
        return x

    #everything regarding the help command was made by bottersnike and hanss
    def format_args(self, cmd):
        params = list(cmd.clean_params.items())
        p_str = ''
        for p in params:
            if p[1].default == p[1].empty:
                p_str += ' <{}>'.format(p[0])
            else:
                p_str += ' [{}]'.format(p[0])

        return p_str

    def format_commands(self, prefix, cmd, name=None):
        cmd_args = self.format_args(cmd)
        if not name: name = cmd.name
        name = name.replace('  ', ' ')
        d = '`{}{}{}`\n'.format(prefix,name,cmd_args)

        if type(cmd) == commands.core.Group:
            cmds = sorted(list(cmd.commands), key=lambda x: x.name)
            for subcmd in cmds:
                d += self.format_commands(prefix, subcmd, name='{} {}'.format(name,subcmd.name))

        return d

    def get_help(self, ctx, cmd, name=None):
        d = 'Help for command `{}`:\n'.format(cmd.name)
        d += '\n**Usage:**\n'

        d += self.format_commands(ctx.prefix, cmd, name=name)

        d += '\n**Description:**\n'
        d += '{}\n'.format('None' if cmd.brief is None else cmd.brief.strip())

        if cmd.checks:
            d += '\n**Checks:**'
            for check in cmd.checks:
                d += '\n{}'.format(check.__qualname__.split('.')[0])
            d += '\n'

        if cmd.aliases:
            d += '\n**Aliases:**'
            for alias in cmd.aliases:
                d += '\n`{}{}`'.format(ctx.prefix,alias)

            d += '\n'

        return d

    @commands.command()
    async def help(self, ctx, *args):
        '''This help message'''
        if len(args) == 0:
            cats = [cog for cog in self.bot.cogs]
            cats.sort()
            width = max([len(cat) for cat in cats]) + 2
            d = '**Categories:**\n'
            for cat in zip(cats[0::2], cats[1::2]):
                d += '**`{}`**{}**`{}`**\n'.format(cat[0], ' ' * int(2.3 * (width - len(cat[0]))), cat[1])
            if len(cats) % 2 == 1:
                d += '**`{}`**\n'.format(cats[-1])

            d += '\nUse `{0}help <category>` to list commands in a category.\n'.format(ctx.prefix)
            d += 'Use `{0}help <command>` to get in depth help for a command.\n'.format(ctx.prefix)

        elif len(args) == 1:
            cats = {cog.lower(): cog for cog in self.bot.cogs}
            if args[0].lower() in cats:
                cog_name = cats[args[0].lower()]
                d = 'Commands in category **`{}`**:\n'.format(cog_name)
                cmds = self.bot.get_cog(cog_name).get_commands()
                for cmd in sorted(list(cmds), key=lambda x: x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Command not found.'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = self.get_help(ctx, cmd)
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if cmd == ctx.bot and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                elif type(cmd) == commands.Group and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    if cmd == ctx.bot:
                        d += 'Command not found.'
                    else:
                        d += 'No sub-command found.'.format(cmd.name, i)
                    break

            else:
                d = self.get_help(ctx, cmd, name=cmd_name)

        # d += '\n*Made by Bottersnike#3605 and hanss314#0128*'
        return await ctx.send(d)

    @commands.check(owner)
    @commands.command(name="eval", brief="evaluate some code")
    async def _eval(self, ctx, *, code: str):

        try:
            ans = eval(code)
            error = 0
        except Exception as err:
            error = 1
            ans = str(err)
        finally:

            embed = discord.Embed(color=[0x00ff00, 0xff0000][error])
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="Code", value=("```Python\n" + code + "\n```")
                            , inline=False)
            embed.add_field(name=["Result", "Error"][error], value=("```\n" + str(ans) + "\n```")
                            , inline=True)
            await ctx.send(embed=embed)

    @commands.check(owner)
    @commands.command(name="exec", brief="execute some code")
    async def _exec(self, ctx, *, code: str):

        text = code

        if code.startswith("```Python"):
            text = text.replace("```Python", "```")

        text = text[:-3]

        lines = text.split("```")[1].splitlines()
        runningcode = "\n".join(lines)[1:]

        # setup the environment
        old_stdout = sys.stdout
        sys.stdout = io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)

        # do something that writes to stdout or stdout.buffer

        try:
            exec(runningcode)
            sys.stdout.seek(0)  # jump to the start
            ans = sys.stdout.read()  # read output
            error = 0
        except Exception as e:
            ans = str(e)
            error = 1
        finally:
            # restore stdout
            sys.stdout.close()
            sys.stdout = old_stdout

            embed = discord.Embed(color=[0x00ff00, 0xff0000][error])
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="Code", value=("```Python\n" + runningcode + "\n```")
                            , inline=False)
            embed.add_field(name=["Result", "Error"][error], value=("```\n" + str(ans) + "\n```")
                            , inline=True)
            await ctx.send(embed=embed)


    @commands.check(owner)
    @commands.command(brief="Adds `role_2` to everyone with `role_1`")
    async def role_add(self,ctx,role_1 : int,role_2 : int):
        guild = ctx.guild
        r1 = discord.utils.get(guild.roles, id=role_1)
        r2 = discord.utils.get(guild.roles, id=role_2)

        member = guild.get_member(ctx.message.author.id)

        given = 0
        members = 0

        for member in guild.members:
            #print(member.name, member.roles)
            #print(r1,r2)
            if r1 in member.roles:
                print("Adding role to {}".format(member.name))
                await member.add_roles(r2)
                given += 1
            members += 1

        await ctx.send("Role given to {} people.".format(given))

    @commands.check(owner)
    @commands.command(brief="Removes `role_2` from everyone with `role_1`")
    async def role_sub(self, ctx, role_1 : int,role_2 : int):
        guild = ctx.guild
        r1 = discord.utils.get(guild.roles, id=role_1)
        r2 = discord.utils.get(guild.roles, id=role_2)

        member = guild.get_member(ctx.message.author.id)

        given = 0
        members = 0

        for member in guild.members:
            if r1 in member.roles:
                if r2 in member.roles:
                    print("Removing role from {}".format(member.name))
                    await member.remove_roles(r2)
                    given += 1
            members += 1

        await ctx.send("Role taken from {} people.".format(given))

    @commands.check(owner)
    @commands.command(brief="Set signup state")
    async def signup_state(self, ctx, state : bool):
        self.bot.game.can_signup = state
        await ctx.send("Signup state changed to {}".format(state))


    @commands.check(owner)
    @commands.command(brief="Advance to the next phase")
    async def advance_phase(self, ctx):
        self.bot.game.phase = (self.bot.game.phase + 1) % 4
        if self.bot.game.phase == 0:
            self.bot.game.new_round()
        elif self.bot.game.phase == 1:
            self.bot.game.start_voting()
        elif self.bot.game.phase == 2:
            self.bot.game.start_results()


        if self.bot.game.phase != 1:
            channel = self.bot.get_channel(772990099033948160)
            for transaction in self.bot.game.transactions_to_send:
                await channel.send(transaction)

            self.bot.game.transactions_to_send = []

        await ctx.send("Phase changed to {}".format(["responding","voting","results","interphase"][self.bot.game.phase]))


    def get_player_object(self, ctx, given_id, mentions_index=0):
        try:
            pid = ctx.message.mentions[mentions_index].id
        except:
            try:
                pid = int(given_id)
            except:
                raise ValueError("That player is invalid.")

        p = self.bot.game.get_player_from_id(pid)
        if p is None:
            raise ValueError("That player is not a contestant.")

        if not p.alive:
            raise ValueError("That player is dead.")

        return p


    @commands.check(owner)
    @commands.command(brief="Eliminate all ids given")
    async def kill(self, ctx, *ids):
        body_count = 0
        ids = [int(i) for i in ids]
        for i in ids:
            for p in self.bot.game.players:
                if p.id == i:
                    p.alive = False
                    body_count += 1
        await ctx.send("Killed {}.".format(body_count))


    @commands.check(owner)
    @commands.command(aliases=["screensize"],brief="Set screen size")
    async def setscreensize(self, ctx, size : int):
        self.bot.game.screen_size = size
        await ctx.send("Screen size set to {}".format(size))

    @commands.check(owner)
    @commands.command(brief="Reply to a DM")
    async def reply(self, ctx, mention, *, content):
        user = ctx.message.mentions[0]
        await user.send(content)

    @commands.check(owner)
    @commands.command(aliases=["export_results","export"],brief="Get the json file containing the most recently tabulated results.")
    async def extract_results(self, ctx):
        x = self.get_results()
        channel = ctx.message.channel
        await ctx.send(file=discord.File(open("results/results.json","rb")))

    @commands.check(owner)
    @commands.command(aliases=["current_results"],brief="Tabulate the current results if voting were to end now.")
    async def tabulate_results(self, ctx):
        x = self.get_results()
        message = '```\n'
        for response in x:
            message += "{} #{} - {}\n".format(response["player"],response["index"],response["response"])
            message += "μ = {}, σ = {}, s = {}\n".format(response["mean"],response["stdev"],response["skew"])
            message += "metas = {}\n".format(response["metas"])
            message += "Score - {} | Movement - {}\n\n".format(response["score"],response["movement"])

        message += "```"
        await ctx.send(message)

    @commands.check(owner)
    @commands.command(aliases=["boost_add"],brief="Add a boost to a player")
    async def add_boost(self, ctx, player_id : str, boost : float, duration : int, boost_id : str):
        try:
            player = self.get_player_object(ctx,player_id)
        except ValueError as e:
            return await ctx.send(e)

        player.score_boosts.append([boost,duration,boost_id])
        await ctx.send("Given `{}` of {} to {} for {} rounds".format(boost_id,boost,self.bot.get_name(player.id),duration))

    @commands.check(owner)
    @commands.command(aliases=["boost_remove"],brief="Remove a boost from a player")
    async def remove_boost(self, ctx, player_id : str, boost_id : str):
        try:
            player = self.get_player_object(ctx,player_id)
        except ValueError as e:
            return await ctx.send(e)

        old_length = len(player.score_boosts)
        player.score_boosts = [i for i in player.score_boosts if i[2] != boost_id]
        new_length = len(player.score_boosts)

        await ctx.send("Removed all boosts with id `{}` ({} item(s) removed)".format(boost_id,old_length-new_length))

    @commands.check(owner)
    @commands.command(brief="Give a player more or less responses [lasts indefinitely!]")
    async def update_response_count(self, ctx, player_id : str, amount : int):
        try:
            player = self.get_player_object(ctx,player_id)
        except ValueError as e:
            return await ctx.send(e)

        player.update_max_responses(amount)
        return await ctx.send("Set {}'s max responses to {}.".format(self.bot.get_name(player.id),amount))

    @commands.check(owner)
    @commands.command(aliases=["item_give"],brief="Give a player an item")
    async def give_item(self, ctx, player_id : str, item_id : str):
        try:
            player = self.get_player_object(ctx, player_id)
        except ValueError as e:
            return await ctx.send(e)

        try:
            item = self.bot.game.new_player_item(item_id)
        except:
            return await ctx.send("That is not an item.")

        player.inventory.append(item)
        message = "Given item {} to {}".format(item_id, self.bot.get_name(player.id))
        self.bot.game.transactions_to_send.append(message)
        self.bot.game.all_transactions.append(message)
        self.bot.game.dump_game()

        return await ctx.send(message)


    @commands.check(owner)
    @commands.command(aliases=["item_remove"],brief="Give a player an item")
    async def remove_item(self, ctx, player_id : str, item_uuid : int):
        try:
            player = self.get_player_object(ctx,player_id)
        except ValueError as e:
            return await ctx.send(e)



        removed_item = player.remove_item_with_uuid(item_uuid)
        self.bot.game.dump_game()

        if removed_item is None:
            return await ctx.send("That player did not have that item.")
        else:
            message = "Removed item {} from {}".format(removed_item["name"],self.bot.get_name(player.id))
            self.bot.game.transactions_to_send.append(message)
            self.bot.game.all_transactions.append(message)
            return await ctx.send("Removed item.")

    @commands.check(owner)
    @commands.command(aliases=["trade"],brief="Move an item between two players")
    async def move_item(self, ctx, player_one_id : str, player_two_id : str, item_uuid : int):
        try:
            player_one = self.get_player_object(ctx,player_one_id,0)
        except ValueError as e:
            return await ctx.send(e)

        try:
            player_two = self.get_player_object(ctx, player_two_id, 1)
        except ValueError as e:
            return await ctx.send(e)


        p1name = self.bot.get_name(player_one.id)
        p2name = self.bot.get_name(player_two.id)

        removed_item = player_one.remove_item_with_uuid(item_uuid)

        if removed_item is None:
            return await ctx.send("{} did not have that item.".format(p1name))

        player_two.inventory.append(removed_item)
        self.bot.game.dump_game()

        message = "Moved item {} from {} to {}".format(removed_item["name"],p1name,p2name)
        self.bot.game.transactions_to_send.append(message)
        self.bot.game.all_transactions.append(message)
        return await ctx.send("Moved item {} from {} to {}".format(item_uuid,p1name,p2name))

    @commands.command(aliases=["get_inventory","pinventory"],brief="View any player's inventory (includes 'forbidden knowledge', such as item UUIDs).")
    async def get_player_inventory(self, ctx, player_id):
        try:
            player = self.get_player_object(ctx,player_id)
        except ValueError as e:
            return await ctx.send(e)

        message = "{} currently has the following item(s):\n".format(self.bot.get_name(player.id))
        for i in player.inventory:
            message += self.bot.game.item_string(i) + "\n"
        if len(player.inventory) == 0:
            message += "[No items.]"
        return await ctx.send(message)

    @commands.command(brief="Modify a field of an item.")
    async def modify_item_field(self, ctx, player_id : str, item_uuid : int, field_id : str, new_value : int):
        try:
            player = self.get_player_object(ctx, player_id)
        except ValueError as e:
            return await ctx.send(e)

        item = player.get_item(item_uuid)
        if item is None:
            return await ctx.send("That player did not have that item.")
        else:
            for f in item["fields"]:
                if f["id"] == field_id:
                    f["value"] = new_value
                    return await ctx.send("Set {} to {}".format(field_id,new_value))
            return await ctx.send("That item did not have that field.")

    @commands.check(owner)
    @commands.command(brief="Update the item registry.")
    async def update_item_registry(self,ctx):
        self.bot.game.update_item_registry()
        await ctx.send("Updated.")

    @commands.check(owner)
    @commands.command(brief="get a file mapping IDs to the current player names [used for aesthetic generation].")
    async def export_names(self,ctx):
        with open("names.json","w+") as f:
            json.dump(self.bot.names,f)

        await ctx.send(file=discord.File(open("names.json","rb")))




def setup(bot):
    bot.add_cog(Admin(bot))