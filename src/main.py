import discord
import json
import re
import os

os.system("")

colors = {
        "end": "\x1b[0m",
        "gray": "\x1b[90m",
        "bold_gray": "\x1b[90;1m",
        "cyan": "\x1b[36m",
        "red": "\x1b[31m",
        "dark_red": "\x1b[31;2m",
        "dark_blue": "\x1b[34;2m",
        "green": "\x1b[32m",
        "blue": "\x1b[34m",
        "white": "\x1b[0m",
        "magenta": "\x1b[35m"
    }
output_roles = {
    "system": f"{colors["blue"]}<system>{colors["end"]}",
    "error": f"{colors["dark_red"]}<error>{colors["end"]}",
    "info": f"{colors["cyan"]}<info>{colors["end"]}",
    "warning": f"{colors["magenta"]}<warning>{colors["end"]}"
}

def mark(text: str, color = "green"):
    return f"{colors[color]}{text}{colors['end']}"

def tag(id):
    return f"<@{id}>"

settings: dict

def load_settings():
    global settings
    settings = json.load(open("src/settings.json", "r"))

    #fixing settings responses
    def replace_placeholder(setting: str, pattern = r"<[a-z]+_*[a-z]*>"):
        print(f"{output_roles['system']} Replacing placeholders in {mark(setting)}...", end = " ")
        for response in settings[setting]:
            cases = re.finditer(pattern, settings[setting][response])
            for case in cases:
                settings[setting][response] = settings[setting][response].replace(case.group(), settings[case.group().replace("<", "", 1).replace(">", "", 1)], 1)
        print("done")
    replace_placeholder("default_replies")
    replace_placeholder("commands")

load_settings()

client = discord.Client(intents=discord.Intents.all()) # for now redundant: "command_prefix=">" ,""

@client.event
async def on_ready():
    print(f"{output_roles["system"]} Bot connected as {mark(settings["bot_name"].upper())}")

@client.event   
async def on_message(message):
    Admin_role = discord.utils.get(message.guild.roles, name="admin")
    text = message.content.lower()
    if message.author != client.user and settings["ignore_command"] not in text:
        if settings["censor_list_enforce"]:
            for banned_expression in settings["censor_list"]:
                if banned_expression in text:
                    if settings["show_info"]: print(f"{output_roles["info"]} {mark("Removed", "red")} message: {mark(text, "gray")} by user {mark(message.author)} {mark("(censor list enforced)", "magenta")}")
                    await message.delete()
                    return
        if settings["bot_name"].lower() in text:
            if settings["show_info"]: print(f"{output_roles["info"]} Detected {mark("message", "red")}: {mark(text, "gray")} by user: {mark(message.author)}")
            for response in settings["default_replies"]:
                if response.replace(settings["bot_name"].lower(), "").lower() in text:
                    await message.reply(settings["default_replies"][response].replace("[user]", str(message.author)))
        elif text.startswith(settings["command_prefix"]*2):
            if Admin_role in message.author.roles:
                print(f"{output_roles['info']} Detected {mark("super-command", "red")}: {mark(text.replace(settings["command_prefix"], "").strip(), "gray")} by user {mark(message.author)}")
                if "reload settings" in text:
                    print(f"{output_roles["system"]} Reloading settings...")
                    load_settings()
                    await message.reply("Updated values loaded successfully")
                elif "settings" in text:
                    await message.reply(str(settings))
                elif "tag_test" in text:
                    await message.channel.send(f"{tag(message.author.id)}")
            else:
                print(f"{output_roles['warning']} {mark("UNAUTHORIZED", "red")} super-command attempt by {mark(message.author)} => {mark(text, "gray")}")
        elif text.startswith(settings["command_prefix"]):
            if settings["show_info"]: print(f"{output_roles['info']} Detected {mark("command", "red")}: {mark(text.replace(settings["command_prefix"], "").strip(), "gray")} by user {mark(message.author)}")
            if "dm help" in text:
                mentions = message.mentions
                await message.delete()
                await message.channel.send(f"{message.author.global_name} seems like a standup guy, maybe you should chat... {tag(mentions[0].id)}")
            else:
                for command in settings["commands"]:
                    if command in text:
                        await message.reply(settings["commands"][command])

client.run(settings["token"])