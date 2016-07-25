from discord.ext import commands

import asyncio, os, urllib.request, laxative, random

class Administrative:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def clone(self, ctx):
        try:
            clonee = ctx.message.mentions[0]
            await self.bot.change_nickname(ctx.message.server.me, clonee.display_name)
            print(clonee.avatar_url)
            fname = clonee.avatar_url.split('/')
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers = {'User-Agent': user_agent,}
            edited_url = 'https://cdn.discordapp.com/avatars/' + fname[len(fname) - 3] + '/' + fname[len(fname) - 1]
            print(edited_url)
            full = os.path.join('files', 'stolen_avatars', fname[len(fname) - 1])

            request = urllib.request.Request(url=edited_url, headers=headers)
            response = urllib.request.urlopen(request)
            with open(full, 'b+w') as f:
                f.write(response.read())
            with open(full, 'rb') as fp:
                await self.bot.edit_profile(password=laxative.credentials['discord']['password'], avatar=fp.read())
        except IndexError:
            await self.random_avatar(ctx)

        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def nick(self, ctx, *, nickname: str=None):
        await self.bot.change_nickname(ctx.message.server.me, nickname)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def avatar(self, ctx):
        await self.random_avatar(ctx)
        await self.bot.delete_message(ctx.message)

    async def random_avatar(self, ctx):
        twitter_pics = os.path.join('files', 'twitter_pics')
        users = os.listdir(twitter_pics)
        user = users[random.randrange(0, len(users))]
        user_folder = os.path.join(twitter_pics, user)
        pics = os.listdir(user_folder)
        pic = pics[random.randrange(0, len(pics))]
        with open(os.path.join(user_folder, pic), 'rb') as fp:
            await self.bot.edit_profile(password=laxative.credentials['discord']['password'], avatar=fp.read())
            await self.bot.change_nickname(ctx.message.server.me, None)

def setup(bot):
    bot.add_cog(Administrative(bot))