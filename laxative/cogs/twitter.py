from discord.ext import commands
import laxative, tweepy, html, urllib.request, os, requests, bs4, re, discordutils, twitutils, linkutils

dir_pics = os.path.join(os.path.expanduser('~'), 'Pictures', 'twitter_pics')


class Twitter:

    def __init__(self, bot):
        info = laxative.credentials['twitter']
        auth = tweepy.OAuthHandler(info['client_key'], info['client_secret'])
        auth.set_access_token(info['access_token'], info['access_secret'])

        self.api = tweepy.API(auth)
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self):
        await self.bot.say('Test')

    @commands.command(pass_context=True)
    async def rip(self, ctx, id_status:str):
        """
        Downloads images to local storage and uploads to the chat.
        """
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        fnames = self.download(status)
        await self.upload(fnames)

    @commands.command(pass_context=True)
    async def dl(self, ctx, id_status:str):
        """
        Downloads images to local storage.
        """
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        self.download(status)

    @commands.command(pass_context=True)
    async def scrape(self, ctx, id_user:str):
        """
        Downloads all accessible images in a user's timeline to local storage.
        """
        await self.bot.delete_message(ctx.message)

        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            self.download(status)

        await self.bot.say('Complete')


    @commands.command(pass_context=True)
    async def save(self, ctx, id_user:str):
        """
        Posts all accessible statuses in a user's timeline to the chat.
        """
        await self.bot.delete_message(ctx.message)
        #for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            #await self.post(status)

    @commands.command(pass_context=True)
    async def retrieve(self, ctx, id_user:str):
        """
        Downloads all accessible images in a user's timeline to local storage and uploads to the chat.
        """
        await self.bot.delete_message(ctx.message)
        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            await self.upload(self.download(status))

    @commands.command(pass_context=True)
    async def get(self, ctx, id_status:str):
        """
        Posts a status to the chat.
        """
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        #await self.post(status)

    @commands.command(pass_context=True)
    async def url(self, ctx, id_status:str):
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)

        for url in status.entities['urls']:
            await self.bot.say(url['expanded_url'])

    @commands.command(pass_context=True)
    async def insta(self, ctx, link:str):
        await self.bot.delete_message(ctx.message)
        await self.bot.say(linkutils.get_insta(link))

    @commands.command(pass_context=True)
    async def ameblo(self, ctx, link:str):
        await self.bot.delete_message(ctx.message)
        for pic in linkutils.get_ameblo(link):
            await self.bot.say(pic)

    @commands.command(pass_context=True)
    async def tweet(self, ctx, id_status:str):
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        await self.bot.say(embed=discordutils.encode_status(status))

    def parse_input(self, id_status):
        id = id_status.split('/')
        status = self.api.get_status(id[len(id) - 1])
        return status

    def download(self, status):
        if twitutils.is_retweet(status):
            return self.download(status.retweeted_status)
        else:
            folder = status.user.id_str
            fn = status.id_str
            fnames = []
            try:
                num = 1
                if not os.path.exists(os.path.join(dir_pics, folder)):
                    os.makedirs(os.path.join(dir_pics, folder))
                for link in twitutils.get_links(status):
                    print(link)
                    ext = link.split('.')
                    fname = fn + '-' + str(num) + '.' + ext[len(ext) - 1]
                    full = os.path.join(dir_pics, folder, fname)
                    if not os.path.exists(full):
                        if link.find('pbs.twimg.com') != -1:
                            urllib.request.urlretrieve(link + ':orig', full)
                        else:
                            urllib.request.urlretrieve(link, full)

                    num += 1

                    fnames.append(full)
            except AttributeError:
                pass

            return fnames

    async def upload(self, fnames):
        for item in fnames:
            try:
                await self.bot.upload(fp=item)
            except Exception:
                pass


def setup(bot):
    bot.add_cog(Twitter(bot))


