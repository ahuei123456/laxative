from discord.ext import commands
import os, json

information = 'Laxatives'

extensions = {'cogs.twitter'}
bot = commands.Bot(description=information, self_bot=True, command_prefix=commands.when_mentioned_or('$'))


def load_credentials():
    path = os.path.join(os.getcwd(), 'files', 'credentials.json')
    with open(path) as f:
        return json.load(f)


credentials = load_credentials()

if __name__ == "__main__":
    for extension in extensions:
        bot.load_extension(extension)

    token = credentials['discord']['token']

    while True:
        try:
            bot.run(token, bot=False)
        except Exception:
            pass