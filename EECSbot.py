import discord, asyncio, praw
from random import choice
from discord.ext import commands

reddit = praw.Reddit(client_id='ZBOaap1b2HZmkg',
                     client_secret='0IrpKpbgokcqv91ykb_Ae1jlcbk',
                     user_agent='Reddit Scraper for DiscordBot v 0.1 by /u/theeashman')
client = commands.Bot(description='EecsBot for EECSQuarter Discord Chat', command_prefix='>')

userinfo = {}

def newusersub(username):
    for submission in reddit.redditor(username).submissions.new(limit=1):
        if userinfo[username][0] != submission.title:
            userinfo[username] = [submission.title, submission.url, 'Continue the Discussion: ' + submission.shortlink]
            return True #this part is a hacky fix so that it doesnt keep resending the message, but im lazy.
        else:
            return False

async def reddit_checker():
    await client.wait_until_ready()
    while not client.is_closed:
        for i in range(len(list(userinfo))):
            if newusersub(list(userinfo)[i]):
                for j in range(len(userinfo[list(userinfo)[i]])):
                    await client.send_message(client.get_channel('306599926492692491'), userinfo[list(userinfo)[i]][j])
        await asyncio.sleep(60)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message.channel)
    if 'eecs' in message.content and 'meme' in str(message.channel):
        eecs_copypasta = ['http://eecseecs.com/meme.html', 'What the fuck did you just fucking say about me, you little humanities major? I’ll have you know I place in the top 5% of my EECS classes, and I’ve been involved in numerous successful startups, and I have over 3000 github repositories. I am trained in algorithms and circuit analysis and I’m the top data structure master in the entire Berkeley EECS community. You are nothing to me but just another bug. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with stoping my code from compiling? Think again, fucker. As we speak I am contacting my secret network of HKN associates across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can corrupt your hard drive in over seven hundred ways, and that’s just with the shit I learned in the CS61 series. Not only am I extensively trained in fourier analysis, but I have access to the entire arsenal of the hive servers and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will destroy the curve and you will drown in it. You’re fucking dead, kiddo.', 'Sorry but I sexually identify as an EECS major. Ever since I was a high schooler applying to Berkeley, I dreamed of typing up code, dropping Github repositories like no tomorrow. People say to me that a person being an EECS major is impossible and I\'m fucking retarded but I don\'t care, I\'m beautiful. I\'m having a surgeon install Notepad++ and vim in my brain. From now on I want you guys to call me "Anant Sahai" and respect my right to code 24/7. If you can\'t accept me you\'re a hackerphobe and need to check your intellectual privilege. Thank you for being so understanding.', '''Berkeley is 10 thousand high IQ college educated middle class men. If we really wanted to we could invade Stanford and install a new school system. We definitely have the manpower. There are plenty of system admins here. Plus everyone here knows where the "disable firewall" button is, from years of coding.
Realistically the Berkeley EECS Force would be far more effective than half the world's universities. CalTech is too busy tanning at the beach. MIT is on the East Coast, the ping is high enough that we can react to them breaking into our servers. Plus Stanford has only 8 thousand 1337 hackers, the majority of whom are useless paper pushers.
I don't actually support the violent overthrow of Stanford. I just think its kind of a fun idea conceptualy.''', '''First they came for Womens' Studies and I did not speak out because I wasn't a hippie
Then they came for Pre-med and I did not speak out because I didn't want to be a doctor
Then they came for Pre-Haas and I did not speak out because I had no interest in business
Finally they came for me and the rest of the EECS majors were too socially awkward to speak for me''']#im a horrible person
        await client.send_message(message.channel, choice(eecs_copypasta))
    await client.process_commands(message)

@client.command()
async def addredditor(username:str):
    await client.say('I will now track submissions by ' + username)
    userinfo[username] = [1,2]

client.loop.create_task(reddit_checker())
client.run('MzI4NzQ2MjU1NjMzMjE5NTg1.DDIakg.azQAmtp1SS4E76QpGUZs2ZMxMYM')
