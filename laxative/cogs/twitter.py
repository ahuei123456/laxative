from discord.ext import commands
import laxative, tweepy, html, urllib.request, os, requests, bs4, re

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
        for status in tweepy.Cursor(self.api.user_timeline, id=id_user).items():
            await self.post(status)

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
        await self.post(status)

    @commands.command(pass_context=True)
    async def url(self, ctx, id_status:str):
        await self.bot.delete_message(ctx.message)
        status = self.parse_input(id_status)

        for url in status.entities['urls']:
            await self.bot.say(url['expanded_url'])

    @commands.command(pass_context=True)
    async def insta(self, ctx, link:str):
        await self.bot.delete_message(ctx.message)
        await self.bot.say(self.get_insta(link))

    @commands.command(pass_context=True)
    async def ameblo(self, ctx, link:str):
        await self.bot.delete_message(ctx.message)
        for pic in self.get_ameblo(link):
            await self.bot.say(pic)

    def parse_input(self, id_status):
        id = id_status.split('/')
        status = self.api.get_status(id[len(id) - 1])
        return status

    def download(self, status):
        if self.is_retweet(status):
            return self.download(status.retweeted_status)
        else:
            folder = status.user.id_str
            fn = status.id_str
            fnames = []
            try:
                num = 1
                if not os.path.exists(os.path.join(dir_pics, folder)):
                    os.makedirs(os.path.join(dir_pics, folder))
                for link in self.get_links(status):
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
            send += link + '\n'

        await self.bot.say(send.strip())

    def get_links(self, status):
        links = []
        try:
            if hasattr(status, 'extended_entities') and 'media' in status.extended_entities.keys():
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
                                if br > bitrate:
                                    bitrate = br
                                    index = i

                        links.append(videos[index]['url'])
            for link in status.entities['urls']:
                ext = link['expanded_url']
                if ext.find('www.instagram.com') != -1:
                    links.append(self.get_insta(ext))
                elif ext.find('ameblo.jp') != -1:
                    for link in self.get_ameblo(ext):
                        links.append(link)

        except AttributeError:
            pass

        return links


    def is_retweet(self, status):
        return hasattr(status, 'retweeted_status')

    def get_insta(self, insta_link: str):
        r = requests.get(insta_link)
        html = r.content
        soup = bs4.BeautifulSoup(html, 'html.parser')
        food = soup.find_all('meta')
        link = ''
        for item in food:
            try:
                if item['property'] == 'og:image':
                    link = item['content']
                    link = link.split('?ig_cache_key')[0]
                if item['property'] == 'og:video':
                    link = item['content']
            except AttributeError:
                pass
            except KeyError:
                pass

        return link

    def get_ameblo(self, ameblo_link: str):
        r = requests.get(ameblo_link)
        html = r.content
        soup = bs4.BeautifulSoup(html, 'html.parser')

        food = soup.find_all('a')

        links = list()
        for item in food:
            try:
                if 'detailOn' in item['class']:
                    for child in item.children:
                        image = child['src'].split('?')[0]
                        image = image.sub('', 't\d*_')
                        links.append(image)
            except KeyError:
                pass

        return links

    def get_vine(self, vine_link: str):
        pass


def setup(bot):
    bot.add_cog(Twitter(bot))


