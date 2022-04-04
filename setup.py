import os
import discord

env = os.getenv 

address = "http://192.168.0.104:5000"
host = "0.0.0.0"
port = 5000

application_id = 947529373404266548
default_prefix = "."
version = "1.0.0"

production = False

invite_with_identify = f"https://discord.com/api/oauth2/authorize?client_id={application_id}&permissions=8&redirect_uri={address}/return&response_type=code&scope=bot%20applications.commands%20identify%20guilds"
identify = f"https://discord.com/api/oauth2/authorize?client_id={application_id}&permissions=8&redirect_uri={address}/return&response_type=code&scope=identify%20guilds"

client_secret = env("client_secret")

slash_guild = discord.Object(450914634963353600)

embed = 0x2F3136
embedFail = 0xFF0000
embedSuccess = 0x32CD32