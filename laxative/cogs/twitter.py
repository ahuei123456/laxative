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

        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            self.download(status)

        await self.bot.say('Complete')

    @commands.command(pass_context=True)
    async def save(self, ctx, id_user:str):
        await self.bot.delete_message(ctx.message)
        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            await self.post(status)

    @commands.command(pass_context=True)
    async def retrieve(self, ctx, id_user:str):
        await self.bot.delete_message(ctx.message)
        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            await self.upload(self.download(status))

    @commands.command(pass_context=True)
    async def get(self, ctx, id_status:str):
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)
        await self.post(status)

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
            for link in self.get_links(status):
                print(link)
                fname = link.split('/')
                full = os.path.join(dir_pics, folder, fname[len(fname) - 1])
                if not os.path.exists(full):
                    urllib.request.urlretrieve(link, full)

                fnames.append(full)
            """
            for media in status.extended_entities['media']:
                print(media['media_url'])
                fname = media['media_url'].split('/')
                full = os.path.join(dir_pics, folder, fname[len(fname) - 1])
                if not os.path.exists(full):
                    urllib.request.urlretrieve(media['media_url'], full)

                fnames.append(full)
            """
        except AttributeError:
            pass

        return fnames

    async def upload(self, fnames):
        for item in fnames:
            await self.bot.upload(fp=item)

    async def post(self, status):
        user = html.unescape(status.user.name)
        created = str(status.created_at) + ' UTC'
        text = ''
        if self.is_retweet(status):
            text += html.unescape('RT {0.user.name}: {0.text}'.format(status.retweeted_status))
        else:
            text += html.unescape(status.text)
        send = "{} - Tweet by {}: {}\n".format(created, user, text)

        for link in self.get_links(status):
            send += link + ' '

        await self.bot.say(send.strip())

    def get_links(self, status):
        links = []
        try:
            for media in status.extended_entities['media']:
                if not media['type'] == 'video':
                    links.append(media['media_url'])
                else:
                    videos = media['video_info']['variants']
                    bitrate = 0
                    index = 0
                    for i in range(0, len(videos)):
                        if videos[i]['content_type'] == 'video/mp4':
                            br = int(videos[i]['bitrate'])
                            print(br)
                            if br > bitrate:
                                bitrate = br
                                index = i

                    links.append(videos[index]['url'])
        except AttributeError:
            pass

        return links


    def is_retweet(self, status):
        return hasattr(status, 'retweeted_status')


def setup(bot):
    bot.add_cog(Twitter(bot))


