import discord, asyncio, praw, os, psycopg2
import urllib.parse as urlparse
from random import choice
from discord.ext import commands

reddit = praw.Reddit(client_id=os.environ.get('rclientid'),
                     client_secret=os.environ.get('rclientsecret'),
                     user_agent=os.environ.get('useragent'))
client = commands.Bot(description='Reddit Tracker Bot for Discord', command_prefix='>')

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

subscriptions = []

count=0
def init_connect():
    global count
    try:
        count+=1
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor()
        cur.execute("SELECT tracks FROM backup")
        
        
        for i in range(cur.rowcount):
            subscriptions.append(createtrack(cur.fetchone()[0]))
    
        cur.close()
        conn.close()
    except:
        if count <= 10: #try at least 10 times to establish connection
            init_connect()
        else:
            count = None
            pass

def getTableInfo(command):
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()
    cur.execute(command)
    sqlResult = cur.fetchall()
    cur.close()
    conn.close()
    return sqlResult

def runSQLCommand(command, val):
    con = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur=con.cursor()
    cur.execute(command, (val, ))
    con.commit()
    cur.close()
    con.close()

class subscription:
    def __init__(self, tracking, channel, server):
        self.tracking = tracking
        self.channel = channel
        self.server = server
        self.type = None
    
    def latestsub(self):
        raise NotImplementedError()

class usersubmission(subscription):
    def __init__(self, tracking, channel, server):
        super().__init__(tracking, channel, server)
        self.title = None
        self.url = None
        self.shortlink = None
        self.type = 'submissions'

    async def printformatted(self):                       
        message = await client.send_message(client.get_channel(self.channel), self.url)
        await asyncio.sleep(4)
        print(len(message.embeds))
        discordembed = message.embeds[0]

        em = discord.Embed(description=self.title, thumbnail=discordembed['thumbnail'], color=0xDEADBF)
        em.set_author(name=discordembed['title'], url=discordembed['url'])

        em._provider = {
            'url': str(self.shortlink),
            'name': str(self.tracking)
        }

        await client.edit_message(message, new_content=None, embed=em)
        
    def latestsub(self):
        for submission in reddit.redditor(self.tracking).submissions.new(limit=1):
            if self.title != submission.title:
                self.title = submission.title
                self.url = submission.url
                self.shortlink = submission.shortlink
                return True
        return False
                
class usercomment(subscription):
    def __init__(self, tracking, channel, server):
        super().__init__(tracking, channel, server)
        self.author = None
        self.subreddit = None
        self.body = None
        self.permalink = None
        self.rootsubmission = None
        self.type = 'comments'
    
    async def printformatted(self):

        pr = {
            'url': 'https://reddit.com' + str(self.permalink),
            'name': str(self.tracking)
        }

        em = discord.Embed(title=None, description=self.body, provider=pr, color=0xDEADBF)
        em.set_footer(text='in ' + self.subreddit)
        em.set_author(name=self.rootsubmission.title, url=self.rootsubmission.shortlink)

        print(em)        

        await client.send_message(client.get_channel(self.channel), embed=em)
        
    def latestsub(self):
        for comment in reddit.redditor(self.tracking).comments.new(limit=1):
            if self.permalink != str(comment.permalink(fast=False)):
                self.author = str(comment.author)
                self.subreddit = str(comment.subreddit)
                self.body = str(comment.body)
                self.permalink = str(comment.permalink(fast=False))
                self.rootsubmission = comment.submission
                return True
        return False

class subredditsubmission(subscription):
    def __init__(self, tracking, channel, server):
        super().__init__(tracking, channel, server)
        self.title = None
        self.url = None
        self.shortlink = None
        self.type = 'subreddit'
    
    async def printformatted(self):
        em = discord.Embed(title=self.title,  url=self.url, color=0xDEADBF)
        await client.send_message(client.get_channel(self.channel), embed=em)
        
    def latestsub(self):
        for submission in reddit.subreddit(self.tracking).hot(limit=3):
            if self.title != submission.title:
                self.title = submission.title
                self.url = submission.url
                self.shortlink = submission.shortlink
                return True
        return False
           
def createtrack(sqlrow):
    if sqlrow[0][1] == 'comments':
        return usercomment(sqlrow[0][2],sqlrow[0][0], sqlrow[0][3])
    if sqlrow[0][1] == 'submissions':
        return usersubmission(sqlrow[0][2],sqlrow[0][0], sqlrow[0][3])
    if sqlrow[0][1] == 'subreddit':
        return subredditsubmission(sqlrow[0][2],sqlrow[0][0], sqlrow[0][3])
        
async def reddit_checker():
    await client.wait_until_ready()
    while not client.is_closed:
        for sub in subscriptions:
            try:
                if (sub.latestsub()):
                    await sub.printformatted()
            except Exception as e:
                print(e)
        await asyncio.sleep(15)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if 'eecs' in message.content.lower() and 'meme' in str(message.channel):
        eecs_copypasta = ['http://eecseecs.com/meme.html','''As a member of the EECS community and a part of one of these organizations this is highly offensive. CS classes at UC Berkeley make it their goal to give students a place to feel comfortable as well as better the community. Trivializing their work by comparing specific classes to the humanities is absurd and beyond inaccurate. Making the claim that CS classes are cliques is demeaning the EE and CS they are founded on. This clearly is a stab at a community on campus that does nothing but support the rest of the student body.''','''Dude, this is a serious discord, and should be treated as such. Thousands of students are busting their asses off at this school, and you're making a mockery not only of the students who go to class day after day, paying thousands of dollars for the best education in the world. You can take your half-assed memes about EECS and Guy Fieri to leddit.''', 'What the fuck did you just fucking say about me, you little humanities major? I’ll have you know I place in the top 5% of my EECS classes, and I’ve been involved in numerous successful startups, and I have over 3000 github repositories. I am trained in algorithms and circuit analysis and I’m the top data structure master in the entire Berkeley EECS community. You are nothing to me but just another bug. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with stoping my code from compiling? Think again, fucker. As we speak I am contacting my secret network of HKN associates across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can corrupt your hard drive in over seven hundred ways, and that’s just with the shit I learned in the CS61 series. Not only am I extensively trained in fourier analysis, but I have access to the entire arsenal of the hive servers and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will destroy the curve and you will drown in it. You’re fucking dead, kiddo.', 'Sorry but I sexually identify as an EECS major. Ever since I was a high schooler applying to Berkeley, I dreamed of typing up code, dropping Github repositories like no tomorrow. People say to me that a person being an EECS major is impossible and I\'m fucking retarded but I don\'t care, I\'m beautiful. I\'m having a surgeon install Notepad++ and vim in my brain. From now on I want you guys to call me "Anant Sahai" and respect my right to code 24/7. If you can\'t accept me you\'re a hackerphobe and need to check your intellectual privilege. Thank you for being so understanding.', '''Berkeley is 10 thousand high IQ college educated middle class men. If we really wanted to we could invade Stanford and install a new school system. We definitely have the manpower. There are plenty of system admins here. Plus everyone here knows where the "disable firewall" button is, from years of coding.
Realistically the Berkeley EECS Force would be far more effective than half the world's universities. CalTech is too busy tanning at the beach. MIT is on the East Coast, the ping is high enough that we can react to them breaking into our servers. Plus Stanford has only 8 thousand 1337 hackers, the majority of whom are useless paper pushers.
I don't actually support the violent overthrow of Stanford. I just think its kind of a fun idea conceptualy.''', '''I'm currently at the point where I should be considering my career options after graduating Berkeley EECS. Life goal number one (not life goal number zero - that's to live forever) for me has been to at some point have at least a billion dollars for about as long as I can remember. It seems to me that, given my skill set and interests, the best way for me to do this is by entrepreneuring or perhaps just business-managing in the tech industry. So, as a huge fan of Google, I decided about six months ago that being the CEO of Google is my primary objective in life; I'm smart enough to have a pretty good chance at pulling it off, and there's much less competition to become the CEO of Google than there is to grow your own start-up into a multi-billion-dollar corporation. Everybody wants to start their own company; not many want to take over an existing favorite. Plus, if I fail to become the CEO of Google or decide I don't want to be, I could always try for one of the many other companies I like, or I could still decide to partner with a Haas student (Hasshole lol) to start my own company after all.

I read Huxley's A Brave New World and it really put my thoughts into words. I mean you have the working class that is supposed to do grunt work like homework on Piazza. Big business wants to keep the general public from being rich which is why they stress homework for CS61A students so much. It's supposed to make you think that it's what real life is. And Hilfiger's are even WORSE! Yeah, I can look up any fact I want, but Berkeley EECS just is trying to make us "hampsters" run through loops over and over again to see if we can remember a fist full of facts. I don't care about that. I'm an intellectual and we look what we need to and our intellegence is what puts it all together. I didn't fail Berkeley, Berkeley failed me.''', '''First they came for Womens' Studies and I did not speak out because I wasn't a hippie
Then they came for Pre-med and I did not speak out because I didn't want to be a doctor
Then they came for Pre-Haas and I did not speak out because I had no interest in business
Finally they came for me and the rest of the EECS majors were too socially awkward to speak for me''']#im a horrible person
        await client.send_message(message.channel, choice(eecs_copypasta))
    elif 'cs' in message.content.lower() and 'meme' in str(message.channel):
        cs_copypasta = '''I'd just like to interject for a moment. What you're referring to as CS is actually EE+CS or as I've recently taken to calling it, EECS. CS is not a field all to itself but rather a subdivision of computing theory only made practical by advancements in digital circuitry. Many people today study CS without recognizing its roots in digital logic and signal processing.Through a particular turn of events, the most direct means of interaction most students have with computers today is through programming, and so many are not aware of the fundamental role of electrical engineering in designing them.
There really is a CS and these people are majoring in it, but it is just another layer on top of a more nuanced view of computing. CS is the theory of computation: the field dealing with abstract algorithms and data structures necessary to implement certain logic. CS is a necessary field, but its mathematical theory is useless by itself; it can only be put into practice with the help of microchips designed by electrical engineers to transform analog signals into discrete logic. Practical CS is normally reliant upon on a computer built upon layers and layers of circuitry. The whole field is basically CS built on top of EE, or EECS. All the so-called CS majors are really abstracted EE majors.'''
        await client.send_message(message.channel, cs_copypasta)
    await client.process_commands(message)

@client.command(description='Creates a Track of a user\'s comments, submissions, or a subreddit', pass_context=True)
async def addtrack(msg, targetname:str, reddittype:str):
    if reddittype == 'comments' or reddittype == 'submissions' or reddittype == 'subreddit':
        info=[[str(msg.message.channel.id), reddittype, targetname, str(msg.message.server.id)], ['placeholder', 'another one', 'and anothe one', 'heres one more']]
        
        subscriptions.append(createtrack(info))
        runSQLCommand("INSERT INTO backup (tracks) VALUES (%s)", info)
        await client.say('Tracking ' + targetname + '\'s ' + reddittype)
    else:
        await client.say('Error: Unable to Track')

@client.command(description='Remove a Reddit Track', pass_context=True)
async def removetrack(msg, targetname:str, reddittype:str):
    counter = 0
    for entry in subscriptions:
        if entry.tracking == targetname and entry.type == reddittype:
            counter += 1
            subscriptions.remove(entry)
            data_unique=[[entry.channel, entry.type, entry.tracking, entry.server], ['placeholder', 'another one', 'and anothe one', 'heres one more']]
            runSQLCommand("DELETE FROM backup WHERE tracks = %s", data_unique)
            await client.say('Removed ' + reddittype + ' track of ' + targetname + ' in #' + str(client.get_channel(msg.message.channel.id)))
    if counter == 0:
        await client.say('There was no track matching your arguements.')

@client.command(description='Returns name of redditor and their attribute being tracked.', pass_context=True)
async def tracking(msg):
    counter = 0
    for entry in subscriptions:
        if 'all' in msg.message.content:
            await client.say('Tracking ' + entry.tracking + '\'s ' + entry.type + ' in channel, server ' + entry.channel + ', ' + entry.server)
        elif entry.server == msg.message.server.id:
            counter += 1
            await client.say('Tracking ' + entry.tracking + '\'s ' + entry.type)
    if counter == 0 and 'all' not in msg.message.content:
        await client.say('There are no tracks in this server')

@client.command(description='Prints debugging info containing sql schema and table', pass_context=True, hidden=True)
async def sqlinfo(msg, statement:str):
    try:
        await client.say(getTableInfo(statement))
    except:
        await client.say('Something is fucked bro')

@client.command(description='Eval your python code', pass_context=True, hidden=True)
async def debugeval(msg, statement:str):
    global asdfasdf
    try:
       await client.say(eval(statement))
    except Exception as e: 
        await client.say(e)


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='>help for help'))


init_connect()
[sub.latestsub() for sub in subscriptions]
client.loop.create_task(reddit_checker())
client.run(os.environ.get('dtoken'))