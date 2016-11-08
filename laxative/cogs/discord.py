from discord.ext import commands
from discord.errors import Forbidden, HTTPException

import asyncio, os, urllib.request, laxative, random, discord, datetime, unicodedata

dir_avatars = os.path.join(os.path.expanduser('~'), 'Pictures', 'Discord', 'avatars')
emoji_str = 'regional_indicator_{}'
emoji_uni = ['U0001f1e6', 'U0001f1e7', 'U0001f1e8', 'U0001f1e9']

class Discord:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def kick(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except IndexError:
            return

        await self.bot.say("Kicked {}".format(user.name))

    @commands.command(pass_context=True, no_pm=True)
    async def ban(self, ctx):
        try:
            user = ctx.message.mentions[0]
        except IndexError:
            return

        await self.bot.say("Banned {}".format(user.name))

    @commands.command(name='cloneuser', pass_context=True, no_pm=True, aliases=['clone'])
    async def clone(self, ctx, *, name=None):
        try:
            user = ctx.message.mentions[0]
            filename = await self.get_avatar(user, name)
            await self.change_avatar(filename)
            await self.bot.change_nickname(ctx.message.server.me, user.display_name)

            await self.bot.say("Cloned {}'s name and avatar".format(user.name))
        except IndexError:
            await self.change_avatar('default')
            await self.bot.change_nickname(ctx.message.server.me, None)

            await self.bot.say("Reset name and avatar to default")


    @commands.command(name='nickname', pass_context=True, no_pm=True, aliases=['nick'])
    async def nick(self, ctx, *, nickname: str=None):
        try:
            user = ctx.message.mentions[0]
            nickname = ' '.join(nickname.split()[1:])
        except IndexError:
            user = ctx.message.server.me

        await self.bot.change_nickname(user, nickname)
        await self.bot.say("Changed {}'s nickname to {}".format(user.name, nickname if nickname is not None else user.name))

    @commands.command(name='saveavatar', pass_context=True, aliases = ['sava'])
    async def sava(self, ctx, *, name=None):
        try:
            user = ctx.message.mentions[0]
            name = ' '.join(name.split()[1:])
        except IndexError:
            user = ctx.message.server.me

        await self.get_avatar(user, name)

        await self.bot.say("Saved {}'s avatar as {}".format(user.name, 'jpg' if name is None else name))

    @commands.command(name='changeavatar', aliases = ['cava'])
    async def cava(self, *, name='default'):
        await self.change_avatar(name)
        await self.bot.say('Changed avatar to {}'.format(name))

    @commands.command(name='listavatar', aliases=['lava'])
    async def lava(self):
        pics = os.listdir(dir_avatars)

        msg = ' | '.join(pics)

        await self.bot.say("**Saved avatars**: " + msg)

    async def get_avatar(self, user, name=None):
        print(user.avatar_url)
        fname = user.avatar_url.split('/')
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        edited_url = 'https://cdn.discordapp.com/avatars/' + fname[len(fname) - 3] + '/' + fname[len(fname) - 1]
        print(edited_url)

        if name is None:
            name = fname[len(fname) - 1]
        else:
            name += '.' + fname[len(fname) - 1].split('.')[1]

        full = os.path.join(dir_avatars, name)

        request = urllib.request.Request(url=edited_url, headers=headers)
        response = urllib.request.urlopen(request)
        with open(full, 'b+w') as f:
            f.write(response.read())

        return full

    async def change_avatar(self, name='default'):
        if len(name.split('.')) != 2:
            name = name + '.jpg'
        pics = os.listdir(dir_avatars)

        if name in pics:
            await self.update_avatar(name)
        else:
            await self.update_avatar('default.jpg')

    async def update_avatar(self, name):
        with open(os.path.join(dir_avatars, name), 'rb') as fp:
            await self.bot.edit_profile(password=laxative.credentials['discord']['password'], avatar=fp.read())

    @commands.command(name='tweetchannel', pass_context=True, no_pm=True, aliases=['tchan', 'twitchan', 'tweetchan'])
    async def tweet_channel(self, ctx, channel_name):
        server = ctx.message.server

        role = await self.bot.create_role(server, name=channel_name)

        everyone = discord.PermissionOverwrite(read_messages=False, send_messages=False)
        mine = discord.PermissionOverwrite(read_messages=True)
        channel = await self.bot.create_channel(server, channel_name, (server.default_role, everyone), (role, mine))

        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        overwrite.send_messages = True
        await self.bot.edit_channel_permissions(channel,
                                                discord.utils.get(server.roles, name="Ruby Bot"), overwrite)

        await self.bot.add_roles(ctx.message.author, role)
        await self.bot.say('Created tweet channel {}'.format(channel.mention))

    @commands.command(name='hiddenchannel', pass_context=True, no_pm=True, aliases=['hchan', 'hidchan', 'hiddenchan'])
    async def hidden_channel(self, ctx, channel_name):
        server = ctx.message.server

        role = await self.bot.create_role(server, name=channel_name)

        everyone = discord.PermissionOverwrite(read_messages=False)
        mine = discord.PermissionOverwrite(read_messages=True)
        channel = await self.bot.create_channel(server, channel_name, (server.default_role, everyone), (role, mine))

        await self.mute_channel(channel, server)
        await self.special_bot_perms(channel, server)
        await self.bot.add_roles(ctx.message.author, role)
        await self.bot.say('Created hidden channel {}'.format(channel.mention))

    @commands.command(name="showchannel", pass_context=True, no_pm=True, aliases=['schan', 'showchan'])
    async def enable_read(self, ctx, *, role_name):
        try:
            channel = ctx.message.channel_mentions[0]
            role_name = ' '.join(role_name.split()[1:])
        except IndexError:
            channel = ctx.message.channel

        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        await self.bot.edit_channel_permissions(ctx.message.channel,
                                                discord.utils.get(ctx.message.server.roles, name=role_name), overwrite)
        await self.bot.say('Role {} is now able to read messages in channel {}'.format(role_name, ctx.message.channel.mention))

    @commands.command(name='mutechannel', pass_context=True, no_pm=True, aliases=['mchan', 'mutechan'])
    async def fix_mute(self, ctx):
        await self.mute_channel(ctx.message.channel, ctx.message.server)
        await self.bot.say('Muted perms added to channel {}'.format(ctx.message.channel.name))

    @commands.command(name='deletechannel', pass_context=True, no_pm=True, aliases=['dchan', 'delchan'])
    async def del_channel(self, ctx):
        try:
            channel = ctx.message.channel_mentions[0]
        except IndexError:
            return

        name = channel.name
        server = ctx.message.server

        await self.bot.delete_channel(channel)
        await self.bot.delete_role(ctx.message.server, discord.utils.get(server.roles, name=name))
        await self.bot.say('Deleted channel {}'.format(channel.name))

    @commands.command(name='reaction', pass_context=True, no_pm=True, aliases=['rxn'])
    async def reaction(self, ctx, msg_id: str, rxn: str):

        message = None
        async for msg in self.bot.logs_from(ctx.message.channel, 100, before=datetime.datetime.now()):
            if msg.id == msg_id:
                message = msg
                break

        if message == None:
            await self.bot.say('Could not find message to react to')

        for char in rxn:
            digit = format(ord(char), 'x')
            fmt = 'U{0:>08}'.format(digit)
            await self.bot.add_reaction(message, fmt)

        await self.bot.say('Added reactions to message')

    @commands.command(pass_context=True, no_pm=True)
    async def emoji(self, ctx):
        emojis = self.bot.get_all_emojis()
        for emoji in emojis:
            print(emoji.name)

    @commands.command()
    async def charinfo(self, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 15 characters at a time.
        """

        if len(characters) > 15:
            await self.bot.say('Too many characters ({}/15)'.format(len(characters)))
            return

        fmt = '`\\U{0:>08}`: {1} - {2} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{0}>'

        def to_string(c):
            digit = format(ord(c), 'x')
            name = unicodedata.name(c, 'Name not found.')
            return fmt.format(digit, name, c)

        await self.bot.say('\n'.join(map(to_string, characters)))

    async def mute_channel(self, channel, server):
        has_muted = False
        for role in server.roles:
            if role.name == 'Muted':
                has_muted = True
                break

        if not has_muted:
            await self.create_muted(server)
        else:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.embed_links = False
            overwrite.attach_files = False
            overwrite.create_instant_invite = False
            overwrite.manage_messages = False
            overwrite.send_tts_messages = False
            overwrite.mention_everyone = False
            overwrite.speak = False
            overwrite.use_voice_activation = False
            await self.bot.edit_channel_permissions(channel,
                                                    discord.utils.get(server.roles, name="Muted"), overwrite)

    async def create_muted(self, server):
        muted = await self.bot.create_role(server, name="Muted", permissions=discord.Permissions(permissions=1115136))
        await self.make_muted_perms(server, muted)

    async def make_muted_perms(self, server, muted):
        """This adds muted perms to every channel, easier than getting admins to do it manually"""
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.embed_links = False
        overwrite.attach_files = False
        overwrite.create_instant_invite = False
        overwrite.manage_messages = False
        overwrite.send_tts_messages = False
        overwrite.mention_everyone = False
        overwrite.speak = False
        overwrite.use_voice_activation = False
        for channel in server.channels:
            await self.bot.edit_channel_permissions(channel, muted, overwrite)

    async def special_bot_perms(self, channel, server):
        try:
            overwrite = discord.PermissionOverwrite()
            overwrite.read_messages = True
            await self.bot.edit_channel_permissions(channel,
                                                    discord.utils.get(server.roles, name="Special Bots"), overwrite)
        except Forbidden:
            pass

    @commands.command(name='createrole', pass_context=True, no_pm=True, aliases=['crole'])
    async def create_role(self, ctx, channel_name):
        server = ctx.message.server

        await self.bot.create_role(server, name=channel_name)

def setup(bot):
    bot.add_cog(Discord(bot))