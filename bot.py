# bot.py
import os

import discord
import json
import formfiller
import traceback
from discord.ext import commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.command(name='about', help='Shows bot info')
async def about(ctx):
    await ctx.message.channel.send('Go Kart Prix Bot by Berke Zorlu (bad_fetus#3637). All complaints go to him! Repository: https://github.com/badfetus/gokartprix-bot')
    
@bot.command(name='assign-race', help ='Assigns race URL to channel')
@commands.has_role('admin')
async def assign_race(ctx, signup_link: str):
    race_data = read_json('race data.json')
    channel_id = ctx.message.channel.id
    race_data.update({str(channel_id): signup_link})
    save_json('race data.json', race_data)
    await ctx.message.channel.send('Channel assigned to the given URL.')

   
@bot.command(name='register', help='Registers you to a race')
async def register(ctx):
    race_database = read_json('race data.json')
    race_data = race_database.get(str(ctx.message.channel.id))
    if (race_data is None):
        await ctx.message.channel.send('No race associated with the channel. Please make sure you run this command from the appropriate channel in the Go Kart Prix server. If you are an admin, use the !assign-race command with the URL to the signup page to associate it.')
    else:
        user_database = read_json('user data.json')
        user_data = user_database.get(str(ctx.message.author.id))
        if (user_data is None):
            await ctx.message.channel.send('You need to enter your user data first. Please see DMs for help.')
            await ctx.message.author.create_dm()
            await ctx.message.author.dm_channel.send('Please use !add-info command to enter your data. You need to enter firstname, lastname, email, phone, country. Usage example looks like "!add-info firstname Igor". Enter your data only in here, never directly in the server.')
        else:
            user_fully_registered = True
            error_string = 'You haven\'t added all your data yet. Please use the !add-info command to add the following data: '
            for parameter in user_parameters:
                if user_data.get(parameter) is None:
                    user_fully_registered = False
                    error_string += parameter + ' ' 
            if user_fully_registered:
                submitData(race_data, user_data)
                await ctx.message.channel.send('Registration submitted!')
                await ctx.message.author.create_dm()
                await ctx.message.author.dm_channel.send('Check your e-mail to confirm you have successfully registered. Confirmation e-mail might take up to 5 minutes, and might end up in your spam folder.')
            else:
                await ctx.message.channel.send(error_string)
        
def submitData(race_data, user_data):
    attempt_string = 'Attempting to submit user data with following inputs...: '
    for parameter in user_parameters:
        attempt_string += parameter + ': ' + user_data.get(parameter) + ' | '
    formfiller.submitData(race_data, user_data, user_parameters)

@bot.command(name='details', help='Shows race details')
async def details(ctx):
    race_database = read_json('race data.json')
    race_data = race_database.get(str(ctx.message.channel.id))
    if (race_data is None):
        await ctx.message.channel.send('No race associated with the channel. Please make sure you run this command from the appropriate channel in the Go Kart Prix server. If you are an admin, use the !assign-race command with the URL to the signup page to associate it.')
    else:
        session = HTMLSession()
        res = session.get(race_data)
        soup = BeautifulSoup(res.html.html, "html.parser")
        fullText = soup.get_text()
        split = fullText.splitlines()
        s = 'Race details:\n' + getDate(split) + '\n' + getPlace(split) + '\n' + getGPS(split)
        await ctx.message.channel.send(s)

def getDate(split):
    for s in split:
        if(s.startswith('Date')):
            return s
    return 'Failed to determine time.'
            
def getPlace(split):
    for s in split:
        if(s.startswith('Location')):
            return s
    return 'Failed to determine location.'

def getGPS(split):
    for s in split:
        if(s.startswith('GPS')):
            return s 
    return 'Failed to determine GPS.'
    
@bot.command(name='participants', help='Shows how many people signed up')
async def participants(ctx):
    race_database = read_json('race data.json')
    race_data = race_database.get(str(ctx.message.channel.id))
    if (race_data is None):
        await ctx.message.channel.send('No race associated with the channel. Please make sure you run this command from the appropriate channel in the Go Kart Prix server. If you are an admin, use the !assign-race command with the URL to the signup page to associate it.')
    else:
        session = HTMLSession()
        res = session.get(race_data)
        soup = BeautifulSoup(res.html.html, "html.parser")
        fullText = soup.get_text()
        split = fullText.splitlines()
        s = getParticipantCount(split)
        await ctx.message.channel.send(s)
        
def getParticipantCount(split):
    for s in split:
        if(s.startswith('Attendance')):
            return s 
    return 'Failed to determine participant count.'

user_parameters = ['firstname', 'lastname', 'email', 'phone', 'country']            
@bot.command(name='add-info', help='Adds your racer details to the bot database')
async def add_info(ctx, parameter: str, value: str):
    user_database = read_json('user data.json')
    user_data = user_database.get(str(ctx.message.author.id))
    if(user_data is None):
        user_data = dict()
    
    valid_parameter = False;
    for string in user_parameters:
        if string == parameter:
            valid_parameter = True;
            break;
    if not valid_parameter:
        error_message = 'Parameter ' + parameter + ' not a valid parameter. Valid options are: '
        for string in user_parameters:
            error_message += string + " "
        await ctx.message.channel.send(error_message)
        return
    else:
        user_data.update({parameter: value})
        user_database.update({str(ctx.message.author.id): user_data})
        save_json('user data.json', user_database)
        await ctx.message.channel.send('Saved user ' + parameter + ' as ' + value + '.' )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("A parameter is missing. !add-info command requires 2 parameters, the type of info you are adding and the value. The types you can add are firstname, lastname, email, phone, country.") 
        await ctx.send("Usage example: \"!add-info firstname Igor\"")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.channel.send("I don't know that command")
    else:
        print(error)

def read_json(fileName):
   with open(fileName, 'r') as file:
      return json.load(file)

def save_json(fileName, data):
   with open(fileName, 'w') as file:
      json.dump(data, file, indent=4)
      
def getStageNo():
    return int(read_json('bot data.json').get('nextStage'))
    
def setStageNo(stageNo):
    botData = read_json('bot data.json')
    botData.update({'nextStage': stageNo})
    save_json('bot data.json', botData)

@bot.command(name='set-stage', help ='Sets next stage no.')
@commands.has_role('admin')
async def setNextStageNo(ctx, stageNo: int):
    setStageNo(stageNo)
    await ctx.message.channel.send('Next stage no. set to ' + str(stageNo))

@bot.command(name='standings', help='Shows the top 10 of standings')
async def standings(ctx):
    standingsTable = getTables('https://www.gokartprix.gno.se/2022-season/2022-standings/')[0]
    s = 'Standings: \n'
    for i in range(1, 11):
        if(len(standingsTable) <= i):
            break
        s += standingsTable[i][0] + ". " + standingsTable[i][1] + ": " + standingsTable[i][len(standingsTable[i]) - 2] + " (" + standingsTable[i][len(standingsTable[i]) - 1] + ")\n"
    await ctx.message.channel.send(s)

@bot.command(name='schedule', help='Shows the next 5 races')
async def schedule(ctx):
    table = getTables('https://www.gokartprix.gno.se/2022-season/')[0]
    s = 'Schedule: \n'
    for i in range(getStageNo(), getStageNo() + 5):
        if(len(table) <= i):
            break
        s += table[i][0] + " - " + table[i][2] + ": " + table[i][1] + " (" + table[i][5] + ")\n"
    await ctx.message.channel.send(s)

def getTables(url):
    session = HTMLSession()
    res = session.get(url)
    soup = BeautifulSoup(res.html.html, "html.parser")
    tables = [
        [
            [td.get_text(strip=True) for td in tr.find_all('td')] 
            for tr in table.find_all('tr')
        ] 
        for table in soup.find_all('table')
    ]
    return tables

bot.run(TOKEN)  