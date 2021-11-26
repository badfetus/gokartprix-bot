# bot.py
import os

import discord
import json
import formfiller
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.command(name='about')
async def about(ctx):
    await ctx.message.channel.send('Go Kart Prix Bot by Berke Zorlu (bad_fetus#3637). All complaints go to him!')
    
@bot.command(name='assign-race')
@commands.has_role('admin')
async def assign_race(ctx, signup_link: str):
    race_data = read_json('race data.json')
    channel_id = ctx.message.channel.id
    race_data.update({str(channel_id): signup_link})
    save_json('race data.json', race_data)
    await ctx.message.channel.send('Channel assigned to the given URL.')

   
@bot.command(name='register')
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
            await ctx.message.author.dm_channel.send('Please use !add-racer-data command to enter your data. You need to enter firstname, lastname, email, phone, country. Usage example looks like "!add-racer-data firstname Igor". Enter your data only in here, never directly in the server.')
        else:
            user_fully_registered = True
            error_string = 'You haven\'t added all your data yet. Please use the !add-racer-data command to add the following data: '
            for parameter in user_parameters:
                if user_data.get(parameter) is None:
                    user_fully_registered = False
                    error_string += parameter + ' ' 
            if user_fully_registered:
                submitData(race_data, user_data)
            else:
                await ctx.message.channel.send(error_string)

def submitData(race_data, user_data):
    attempt_string = 'Attempting to submit user data with following inputs...: '
    for parameter in user_parameters:
        attempt_string += parameter + ': ' + user_data.get(parameter) + ' | '
    formfiller.submitData(race_data, user_data, user_parameters)

user_parameters = ['firstname', 'lastname', 'email', 'phone', 'country']            
@bot.command(name='add-racer-data')
async def add_racer_data(ctx, parameter: str, value: str):
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
        
def read_json(fileName):
   with open(fileName, 'r') as file:
      return json.load(file)

def save_json(fileName, data):
   with open(fileName, 'w') as file:
      json.dump(data, file, indent=4)

bot.run(TOKEN)  