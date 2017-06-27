import discord, asyncio, praw

reddit = praw.Reddit(client_id='ZBOaap1b2HZmkg',
                     client_secret='0IrpKpbgokcqv91ykb_Ae1jlcbk',
                     user_agent='Reddit Scraper for DiscordBot v 0.1 by /u/theeashman')
client = discord.Client()

def newusersub(username):
    for submission in reddit.redditor(username).submissions.new(limit=1):
        return([submission.title, submission.url, 'Continue the Discussion: ' + submission.shortlink])

prevtitle = ''
async def reddit_checker():
    await client.wait_until_ready()
    while not client.is_closed:
        global prevtitle
        currtitle = newusersub('Samses94')
        if (prevtitle != currtitle):
            for i in range(len(currtitle)):
                await client.send_message(client.get_channel('266750635557388288'), currtitle[i])
            prevtitle = currtitle
        await asyncio.sleep(60)

client.loop.create_task(reddit_checker())
client.run('MzI4NzQ2MjU1NjMzMjE5NTg1.DDIakg.azQAmtp1SS4E76QpGUZs2ZMxMYM')
