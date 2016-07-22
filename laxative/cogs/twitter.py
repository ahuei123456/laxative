from discord.ext import commands
import laxative, tweepy, html, urllib.request, os

dir_pics = os.path.join(os.getcwd(), 'files', 'twitter_pics')


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
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)

        fnames = self.download(status)

        await self.upload(fnames)

    @commands.command(pass_context=True)
    async def dl(self, ctx, id_status:str):
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        self.download(status)

    @commands.command(pass_context=True)
    async def scrape(self, ctx, id_user:str):
        await self.bot.delete_message(ctx.message)

        tweets = self.api.user_timeline(id=id_user, count=200, include_rts=False)
        for tweet in tweets:
            self.download(tweet)

        oldest = tweets[len(tweets)-1].id - 1

        while len(tweets) > 0:
            tweets = self.api.user_timeline(id=id_user, count=200, include_rts=False, max_id=oldest)

            for tweet in tweets:
                self.download(tweet)
                oldest = tweets[len(tweets) - 1].id - 1

        await self.bot.say('Complete')

    def parse_input(self, id_status):
        id = id_status.split('/')
        status = self.api.get_status(id[len(id) - 1])
        return status

    def download(self, status):
        folder = status.user.id_str
        fnames = []
        try:
            if not os.path.exists(os.path.join(dir_pics, folder)):
                os.makedirs(os.path.join(dir_pics, folder))
            for media in status.extended_entities['media']:
                print(media['media_url'])
                fname = media['media_url'].split('/')
                full = os.path.join(dir_pics, folder, fname[len(fname) - 1])
                if not os.path.exists(full):
                    urllib.request.urlretrieve(media['media_url'], full)

                fnames.append(full)
        except AttributeError:
            pass

        return fnames

    async def upload(self, fnames):
        for item in fnames:
            await self.bot.upload(fp=item)


def setup(bot):
    bot.add_cog(Twitter(bot))


