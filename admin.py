import discord
from discord.ext import commands


owner = lambda ctx: ctx.author.id in [137001076284063744,223201675186274304,473975633014161419]

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
                cmds = self.bot.get_cog_commands(cog_name)
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


    '''
    Supervoter 564475422033838080
Superdupervoter 564475556725260308
Supervoter V 569333309662822410
Supervoter IV 569333211004665859
Superduperdupervoter 564475831653629968
'''



    @commands.check(owner)
    @commands.command(brief="Add the next supervoter role to a person.")
    async def supervoter(self, ctx, user_mention):
        supervoter_hierarchy = [
            564475422033838080,
            564475556725260308,
            564475831653629968,
            569333211004665859,
            569333309662822410,
            577274482117574658,
            577274557552132117,
            577274768831545358,
            577274922347266048,
            577275058242846740,
            599635009535475722,
            599635208115060753,
            599635374930788363,
            599635541516091402,
            599635546297467038,
            632303837184524302,
            632303839080480786,
            632303839910821897,
            632303838073847867,
            632303835884290091
        ]


        finished_turn = 567343239913406495

        user = ctx.message.mentions[0]

        role_ids = [i.id for i in user.roles]


        level = len(supervoter_hierarchy)
        for n,rid in enumerate(supervoter_hierarchy):
            if rid not in role_ids:
                await user.add_roles(discord.utils.get(ctx.guild.roles, id=rid))
                await user.add_roles(discord.utils.get(ctx.guild.roles, id=finished_turn))
                level = n
                break


        if level == len(supervoter_hierarchy):
            return await ctx.send("<@137001076284063744> someone supervoted too many times you need to add a new role to the hierarchy")

        else:
            return await ctx.send("{} has been increased in the Supervoter Hierarchy (Now {})".format(user.name, level+1))



def setup(bot):
    bot.add_cog(Admin(bot))