import asyncio
import json
import os
import re
from datetime import datetime
import discord
import requests
from discord.ext import commands, tasks
from selenium import webdriver
import aiohttp
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

executable_path = "chromedriver.exe"
os.environ["webdriver.chrome.driver"] = executable_path
prefix = "!"
intents = discord.Intents.default()
intents.message_content = True
intents.presences = False
intents.members = False
online_auddy = False
bot_commands_channel_id = 1232163578258395170
bot = commands.Bot(command_prefix=prefix, intents=intents)
tries = 0

profiles = [
    {"user": "CarlosH8nriquez", "display": "Agaseis", "ping": "<@&1231760096196034590>", "id": "3849419415", "online": False, "playing": False, "identity": 0},
    {"user": "Auuddy", "display": "Auddy", "ping": "<@&1231438585333415956>", "id": "712699855", "picture": "link", "online": False, "playing": False, "identity": 4},
    {"user": "Chxmei", "display": "Chxmei", "ping": "<@&1231585172923875492>", "id": "1917581866", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "PuddingBumby", "display": "PuddingBumby", "ping": "<@&1231587625903718401>", "id": "1263036254", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "N4Animation", "display": "N4Animation", "ping": "<@&1231594230183497759>", "id": "116174560", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "Megumintx", "display": "Megumint", "ping": "<@&1231595313299718155>", "id": "140375977", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "Oiledmyster", "display": "Ollymyster", "ping": "<@&1231743683880157184>", "id": "1112630598", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "M87Ray", "display": "Guide", "ping": "<@&1239590998678573056>", "id": "273909864", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "Q3Prototype", "display": "Q3", "ping": "<@&1239591791825653881>", "id": "283813432", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "SimpIrr", "display": "Simple", "ping": "<@&1239592371973521448>", "id": "560766989", "picture": "link", "online": False, "playing": False, "identity": 1},
    {"user": "ii_ArunXz", "display": "Kuzma", "ping": "<@&1239593245537730562>", "id": "49142499", "picture": "link", "online": False, "playing": False, "identity": 3},
    {"user": "Hea_vyy", "display": "Heavy", "ping": "<@&1285372603774799952>", "id": "109249716", "picture": "link", "online": False, "playing": False, "identity": 2},
    {"user": "HW5567", "display": "HW", "ping": "<@&1292873491414122549>", "id": "1203375699", "picture": "link", "online": False, "playing": False, "identity": 5},
]

status_map = {
    0: "Offline",
    1: "Online",
    2: "In Game",
    3: "In Studio"
}

def save_cookies(driver, location):
    with open(location, 'w') as filehandler:
        json.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, location):
    with open(location, 'r') as filehandler:
        cookies = json.load(filehandler)
        for cookie in cookies:
            driver.add_cookie(cookie)

def get_user_status(user_id):
    url = "https://presence.roblox.com/v1/presence/users"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "userIds": [user_id]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        presence_data = response.json()
        if presence_data["userPresences"]:
            presence_status = presence_data["userPresences"][0]["userPresenceType"]
            return presence_status
        else:
            return None
    else:
        return None

def get_roblox_user_info(user_id):
    url = f'https://users.roblox.com/v1/users/{user_id}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        username = data.get('name')
        display_name = data.get('displayName')
        return username, display_name
    else:
        return None, None

@bot.command()
async def screenshot(ctx):
    if ctx.channel.id != bot_commands_channel_id:
        return
    screenshot_path = 'screenshot.png'
    driver.get_screenshot_as_file(screenshot_path)
    await ctx.send(file=discord.File(screenshot_path))

@bot.command()
async def addprofile(ctx, user_id: str):
    global tries

    if ctx.channel.id != bot_commands_channel_id:
        await ctx.send("Commands aren't allowed in this channel")
        return

    if tries > 3:
        await ctx.send("Profile list is full at the moment, try later.")
        return
    
    tries += 1

    username, display_name = get_roblox_user_info(user_id)
    
    if username is None:
        await ctx.send("User doesn't exist")
        return
    
    new_profile = {
        "user": username,
        "display": display_name,
        "ping": ctx.author.mention,
        "id": user_id,
        "picture": "link",
        "online": False,
        "playing": False,
        "identity": 5
    }
    
    profiles.append(new_profile)
    
    await ctx.send(f"{new_profile['user']}'s profile added successfully!")

@bot.command()
async def status(ctx):
    if ctx.channel.id != bot_commands_channel_id:
        return
    playing = [p['display'] for p in profiles if p['playing']]
    online = [p['display'] for p in profiles if p['online'] and not p['playing']]
    offline = [p['display'] for p in profiles if not p['online']]

    status_message = (
        f"**• Status •**\n"
        f"**Playing:** {', '.join(playing) if playing else 'None'}\n"
        f"**Online:** {', '.join(online) if online else 'None'}\n"
        f"**Offline:** {', '.join(offline) if offline else 'None'}"
    )

    await ctx.send(status_message)

@bot.command()
async def quit(ctx):
    if ctx.channel.id != bot_commands_channel_id:
        return
    await ctx.send("**| Quitting...**")
    driver.quit()
    os.system("taskkill /f /im chrome.exe")
    os.system("taskkill /f /im chromedriver.exe")
    await bot.close()
    os._exit(0)

@bot.command()
async def commands(ctx):
    if ctx.channel.id != bot_commands_channel_id:
        return
    await ctx.send("!screenshot ⭢ Take a screenshot of bot screen\n!status ⭢ Show up playing/online/offline players\n!quit ⭢ Stop bot execution\n!addprofile (userid) ⭢ Temporarily add a player to profile list")

async def start():
    driver.get("https://www.roblox.com/games/8534845015/ICHIGO-Sakura-Stand#!/game-instances")
    await asyncio.sleep(2)
    driver.execute_script("window.scrollTo(0, 1000)")
    config = driver.find_element(By.ID, "rorsl-settings-button")
    config.click()
    await asyncio.sleep(2)

async def update_online_players():
    while True:
        await asyncio.sleep(120)
        online_players = [p['user'] for p in profiles if p['online']]
        channel = bot.get_channel(1231438296605917337)
        description = f"『 {' '.join(online_players)} 』"
        await channel.edit(topic=description)

async def send_profile_online(bot, driver, profile):
    await asyncio.sleep(2)
    channel = bot.get_channel(1231438296605917337)
    embed = discord.Embed(title=f"**{profile['display']}**", color=discord.Color.from_rgb(245, 0, 0))
    image_element = driver.find_element(By.ID, "rorsl-userImage")
    image = image_element.get_attribute("src")
    profile["picture"] = image
    embed.set_thumbnail(url=image)

    if profile["identity"] == 1:
        embed.set_author(name="Dev", icon_url="https://cdn.discordapp.com/role-icons/986221373850550292/4167f4a4181534357c3f9d8b2f4365a0.webp?size=56&quality=high")
    elif profile["identity"] == 2:
        embed.set_author(name="Game Moderator", icon_url="https://cdn.discordapp.com/role-icons/931511618330820658/2105d69204a0aede77533d94e8023c7d.webp?size=20&quality=high")
    elif profile["identity"] == 3:
        embed.set_author(name="Game Manager", icon_url="https://cdn.discordapp.com/role-icons/931519266077949993/56c96706cd87dbeae8a3410687f0b9bd.webp?size=56&quality=high")
    elif profile["identity"] == 4:
        embed.set_author(name="Owner", icon_url="https://cdn.discordapp.com/role-icons/986220838741245952/cc2d8b1311fa50cb368a5fd725df4070.webp?size=56&quality=high")
    elif profile["identity"] == 5:
        embed.set_author(name="Youtuber", icon_url="https://i.ibb.co/LxTJbjq/1384060.png")
    elif profile["identity"] == 0:
        embed.set_author(name="AvaibleJoin", icon_url="https://i.ibb.co/HYs7NH4/Avaible-Join.png")
    else:
        embed.set_author(name="Player", icon_url="https://i.ibb.co/9ymwZcT/image-7.png")

    embed.add_field(name="Status", value=f"[{profile['user']} is now playing!](https://www.roblox.com/users/{profile['id']}/profile)", inline=False)

    div = driver.find_element(By.XPATH, "//li[contains(@class, 'rorsl-server')][contains(@style, 'border-color: rgb(0, 176, 111)')]")
    join_button = div.find_element(By.XPATH, ".//button[contains(@class, 'btn-full-width')][contains(@class, 'btn-control-xs')][contains(@class, 'rbx-game-server-join')][contains(@class, 'btn-primary-md')]")
    onclick = join_button.get_attribute("onclick")
    pattern = r'Roblox\.GameLauncher\.joinGameInstance\((\d+),\s*"([^"]+)"\)'
    matches = re.search(pattern, onclick)
    gameId = "8534845015"
    serverID = matches.group(2)
    join_link = (f"roblox-player://placeId={gameId}&gameInstanceId={serverID}")
    embed.add_field(name="Server link", value=f"[Click here]({join_link})", inline=False)
    embed.set_footer(text=f"{datetime.now().strftime('%H:%M:%S ・ UTC+3')}", icon_url="https://i.ibb.co/FKqQZdB/checkmark-512.png")
    await channel.send(content=profile['ping'], embed=embed)

async def send_profile_offline(bot, profile):
    channel = bot.get_channel(1231438296605917337)
    embed = discord.Embed(title=f"**{profile['display']}**", color=discord.Color.from_rgb(245, 0, 0))
    embed.set_thumbnail(url=profile["picture"])

    if profile["identity"] == 1:
        embed.set_author(name="Dev", icon_url="https://cdn.discordapp.com/role-icons/986221373850550292/4167f4a4181534357c3f9d8b2f4365a0.webp?size=56&quality=high")
    elif profile["identity"] == 2:
        embed.set_author(name="Game Moderator", icon_url="https://cdn.discordapp.com/role-icons/931511618330820658/2105d69204a0aede77533d94e8023c7d.webp?size=20&quality=high")
    elif profile["identity"] == 3:
        embed.set_author(name="Game Manager", icon_url="https://cdn.discordapp.com/role-icons/931519266077949993/56c96706cd87dbeae8a3410687f0b9bd.webp?size=56&quality=high")
    elif profile["identity"] == 4:
        embed.set_author(name="Owner", icon_url="https://cdn.discordapp.com/role-icons/986220838741245952/cc2d8b1311fa50cb368a5fd725df4070.webp?size=56&quality=high")
    elif profile["identity"] == 5:
        embed.set_author(name="Youtuber", icon_url="https://i.ibb.co/LxTJbjq/1384060.png")
    elif profile["identity"] == 0:
        embed.set_author(name="AvaibleJoin", icon_url="https://i.ibb.co/HYs7NH4/Avaible-Join.png")
    else:
        embed.set_author(name="Player", icon_url="https://i.ibb.co/9ymwZcT/image-7.png")
    
    embed.add_field(name="Status", value=f"[{profile['user']} is not playing anymore!](https://www.roblox.com/users/{profile['id']}/profile)", inline=False)
    embed.add_field(name="Profile Link", value=f"[Click here to check profile](https://www.roblox.com/users/{profile['id']}/profile)", inline=False)
    embed.set_footer(text=f"{datetime.now().strftime('%H:%M:%S ・ UTC+3')}", icon_url="https://i.ibb.co/pZ1Z2FT/R.png")
    await channel.send(content=profile['ping'], embed=embed)

os.environ["webdriver.chrome.driver"] = executable_path

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_extension("serverlist.crx")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1000,1000")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-position=-2400,-2400")
chrome_options.add_argument("--hide-scrollbars")

chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

driver = webdriver.Chrome(options=chrome_options)

@bot.event
async def on_ready():
    game = discord.Game("!commands")
    await bot.change_presence(status=discord.Status.online, activity=game)
    bot.loop.create_task(update_online_players())

    driver.get("https://www.roblox.com/home")

    if os.path.exists('cookies.json'):
        load_cookies(driver, 'cookies.json')
        await asyncio.sleep(2)
        driver.set_window_position(-10000,0)
    else:
        await asyncio.sleep(60)
        save_cookies(driver, 'cookies.json')
        await asyncio.sleep(2)

    await start()

    @tasks.loop(seconds=5)
    async def check_online():
        try:
            for profile in profiles:
                await asyncio.sleep(1)

                status = get_user_status(profile['id'])
                
                if status != 0:
                    profile['online'] = True
                else:
                    profile["online"] = False

                if (profile['online'] and status == 2) or profile["playing"]:
                    input = driver.find_element(By.ID, "rorsl-username")
                    input.clear()
                    input.send_keys(profile['user'])
                    search_button = driver.find_element(By.ID, "rorsl-search")
                    search_button.click()
                    search_status = driver.find_element(By.ID, "rorsl-status")
                    while "Discovering" in search_status.text:
                        await asyncio.sleep(2)
                        search_status = driver.find_element(By.ID, "rorsl-status")
                    status_element = driver.find_element(By.ID, "rorsl-userStatus")
                    status = status_element.text
                    if "!" in status:
                        await asyncio.sleep(1)
                        page_number = ''.join(re.findall(r'\d+', status))
                        page_box = driver.find_element(By.ID, "rorsl-page")
                        page_box.clear()
                        page_box.send_keys(page_number)
                        if not profile["playing"]:
                            await send_profile_online(bot, driver, profile)
                            await asyncio.sleep(1)
                            profile["playing"] = True
                    else:
                        if profile["playing"]:
                            profile["online"] = False
                            profile["playing"] = False
                            await send_profile_offline(bot, profile)
                        continue
            await asyncio.sleep(1)

        except Exception:
            pass
    check_online.start()

bot.run("YOUR DISCORD TOKEN HERE")
