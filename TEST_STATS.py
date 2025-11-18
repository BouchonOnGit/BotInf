import discord
from discord.ext import commands
import json
import os

intents =  discord.intents.default()
intents.message_content = True
intents.reaction = True

bot = commands.Bot(command_prefix="!", intents = intents)

ID_PLAN = #ID DU SALON à compléter

DATA_FILE = plan.json

