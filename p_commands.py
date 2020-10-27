from discord.ext import commands
import discord, random

class PlayerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(brief="Sign up for Board Game TWOW!")
    async def signup(self,ctx):
        if not self.bot.game.can_signup:
            return await ctx.send("You cannot sign up at this time.")

        if ctx.author.id in [i.id for i in self.bot.game.players]:
            return await ctx.send("You have already signed up for Board Game TWOW")

        self.bot.game.add_player(ctx.author.id)
        await ctx.send("You have signed up for Board Game TWOW!")


    @commands.command(aliases=["response"],brief="Submit a response!")
    async def respond(self, ctx, index : int, *, response):
        player = self.bot.game.get_player_from_id(ctx.author.id)

        if player is None:
            return await ctx.send("You are not a contestant.")

        if not player.alive:
            return await ctx.send("You're dead!")

        if self.bot.game.phase != 0:
            return await ctx.send("You cannot respond at this time.")

        if index <= 0: return await ctx.send("That's an invalid index.")
        if index > player.maximum_responses: return await ctx.send("You don't have that many responses.")


        word_count = len(response.split(" "))
        player.add_response(response,index)

        message = "You have submitted\n```\n{}\n``` for response #{}\nYour response is {} words.\n".format(response,index,word_count)

        if word_count > 10: message += "**Your response is more than 10 words long. This is not recommended at all and the voters will almost surely kill you.**\n"
        if word_count < 10: message += "*Your response is fewer than 10 words long. While this is not explicitly forbidden, it is not recommended. Continue at your own risk.*\n"

        message += "Your responding status is:\n"
        for i in range(player.maximum_responses):
            if player.current_responses[i] is not None:
                message += "Response #{}: <:yes:692200347753644084>\n".format(i+1)
            else:
                message += "Response #{}: <:no:692200347732672613>\n".format(i+1)

        return await ctx.send(message)


    @commands.command(brief="Cast your votes!")
    async def vote(self, ctx, user_vote=""):
        if self.bot.game.phase != 1:
            return await ctx.send("You cannot vote at this time.")

        if ctx.author.id not in self.bot.game.voter_registry:
            self.bot.game.voter_registry[ctx.author.id] = {
                "votes" : [],
                "screens" : self.bot.game.generate_screens()
            }

            current_screen = self.bot.game.voter_registry[ctx.author.id]["screens"][0]

            message = "Here is your screen to vote on!\n"
            message += self.bot.game.print_screen(current_screen)
            message += "\nUse `bg!vote` followed your ranking of the responses using the letters on the left!"

            await ctx.send(message)

        else:
            alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

            current_voteamount = len(self.bot.game.voter_registry[ctx.author.id]["votes"])

            if current_voteamount == len(self.bot.game.voter_registry[ctx.author.id]["screens"]):
                return await ctx.send("You've supervoted! There's nothing left to vote on!")

            current_screen = self.bot.game.voter_registry[ctx.author.id]["screens"][current_voteamount]

            if user_vote == "":
                message = "Here is your screen to vote on!\n"
                message += self.bot.game.print_screen(current_screen)
                message += "\nUse `bg!vote` followed your ranking of the responses using the letters on the left!"

                return await ctx.send(message)

            required_letters = alphabet[:len(current_screen)]

            if sorted(user_vote) != required_letters:
                if any(i not in required_letters for i in user_vote):
                    return await ctx.send("That vote is malformed! [Invalid Letters `{}`]".format(" ".join(i for i in user_vote if i not in required_letters)))
                if any(user_vote.count(i) != 1 for i in set(user_vote)):
                    return await ctx.send("That vote is malformed! [Duplicate Letters `{}`]".format(" ".join(i for i in set(user_vote) if list(user_vote).count(i)>1)))
                if any(i not in user_vote for i in required_letters):
                    return await ctx.send("That vote is malformed! [Missing Letters `{}`]".format(" ".join(set(required_letters) - set(user_vote))))
                return await ctx.send("Your vote is invalid for some reason that Bazinga's terrible python didn't account for. Ping him and call him an idiot.")

            vote_list = []
            for i in user_vote:
                vote_list.append(current_screen[alphabet.index(i)])

            self.bot.game.voter_registry[ctx.author.id]["votes"].append(vote_list)
            self.bot.game.master_vote_list.append(vote_list)

            new_voteamount = len(self.bot.game.voter_registry[ctx.author.id]["votes"])

            if new_voteamount == len(self.bot.game.voter_registry[ctx.author.id]["screens"]):
                self.bot.game.dump_game()
                return await ctx.send("Your vote has been recorded! Thank you for supervoting!")

            new_screen = self.bot.game.voter_registry[ctx.author.id]["screens"][new_voteamount]

            message = "Your vote has been recorded!\n**Vote on all screens to stop getting reminders**\nHere is the next screen to vote on, if you wish:\n"
            message += self.bot.game.print_screen(new_screen)
            message += "\nUse `bg!vote` followed your ranking of the responses using the letters on the left!"

            self.bot.game.dump_game()

            await ctx.send(message)

    @commands.command(aliases=["boosts","boost"],brief="Get your current boosts")
    async def get_boosts(self, ctx):
        player = self.bot.game.get_player_from_id(ctx.author.id)

        if player is None:
            return await ctx.send("You are not a contestant.")

        if not player.alive:
            return await ctx.send("You're dead!")

        message = "You currently have the following boost(s):\n```"
        for b in player.score_boosts:
            message += "{} : {}% [Duration - {} round(s)]\n".format(b[2], ("+" if b[0] > 0 else "") + str(b[0]*100), b[1])
        if len(player.score_boosts) == 0:
            message += "You have no boosts."
        message += "```"
        return await ctx.send(message)

    @commands.command(aliases=["items"],brief="Get your current items")
    async def inventory(self, ctx):
        player = self.bot.game.get_player_from_id(ctx.author.id)

        if player is None:
            return await ctx.send("You are not a contestant.")

        if not player.alive:
            return await ctx.send("You're dead!")

        message = "You currently have the following item(s):\n"
        for i in player.inventory:
            message += self.bot.game.item_string(i) + "\n"
        if len(player.inventory) == 0:
            message += "You have no items."
        return await ctx.send(message)

    @commands.command(aliases=["item_use"],brief="Use one of your items.")
    async def use(self, ctx, item_id):
        player = self.bot.game.get_player_from_id(ctx.author.id)

        if player is None:
            return await ctx.send("You are not a contestant.")

        if not player.alive:
            return await ctx.send("You're dead!")

        item = None

        for i in player.inventory:
            if i["id"] == item_id:
                item = i
                break

        if item is None:
            return await ctx.send("You don't have that item!")

        item_data = self.bot.game.get_item_data(item_id)

        if "passive" in item_data["types"]:
            return await ctx.send("That item is passive and cannot be activated!")

        current_use_phase = "svri"[self.bot.game.phase]
        if current_use_phase not in item_data["use_phases"]:
            return await ctx.send("You cannot activate that item at this time!")

        if "persistent" not in item_data["types"]:
            player.inventory.remove(item)
            self.bot.game.dump_game()

        await ctx.send("You have used **{}**!".format(item_data["name"]))

        a = ctx.author
        av = a.avatar_url
        channel = self.bot.get_channel(694724666904018945)
        embed = discord.Embed(name="asdfasdfasfd", color=random.randint(0, 255 ** 3 - 1))
        embed.set_author(name=a.name, icon_url=av)
        embed.add_field(name="Incoming Transmission", value="{} has used {}".format(ctx.author.name, item_data["name"]), inline=True)
        return await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(PlayerCommands(bot))