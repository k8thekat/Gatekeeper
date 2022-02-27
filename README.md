# Gatekeeper Bot 
---
## About
I wanted to create a bot to handle whitelisting of minecraft servers from inside Discord and without any outside user interaction. Simply follow the whitelist format and the bot handles the rest. Then the project turned into what other functionality could I help a community with by allowing user documentation on subjects such as infractions, donations, Minecraft Name, Discord roles and punishments such as a temporary ban without someone having to keep track of when it expires. 

Some additional functionality was added for replying to players with certain keywords or allowing them to check the status of a server, allowing the AMP console to be output to a specific Discord channel, allowing Discord users to talk to players inside of a Minecraft server and allowing staff to control a server inside of Discord.

---
## Requirements

- Currently it is required that the user creates their own bot. 
    - See [Creating a bot Account](https://discordpy.readthedocs.io/en/stable/discord.html), when creating the bot set the [**Bot Permissions**](imgs/bot_perms.png)
- Please Install [Python](https://www.python.org/); you will also need to install the required packages. 
    - **Run `pip install -r requirements.txt`** in the same directory as Gatekeeper Bot.
- You also need to be using [Cube Coders AMP](https://cubecoders.com/AMP) with a instance of Minecraft Java (any version later than 1.12) set up and running.
    - Please set the AMP Role Permissions to [AMP Perms 1](imgs/AMP_perms1.png) and [AMP Perms2](imgs/AMP_perms2.png).

---

## Setup
1. Follow the instructions inside the `tokenstemplate.py file` and `config.py`
2. Run the script via `Powershell` or `Command Prompt`.
3. Once the Bot has connected in any channel type `//setup discord_role_id` or `discord_role_name`. The specified `Discord Role` is now the master Operator/Owner of the Bot. 
    - See [Developer Mode](https://www.howtogeek.com/714348/how-to-enable-or-disable-developer-mode-on-discord/)
4. To see Bot errors, set up **Bot Setting: BotComms**
    - Use the command `//botsetting botcomms discord_channel_id` or `discord_channel_name` to set a channel for bot errors to be sent.
5. Setting up your AMP **Servers**
    - You must enable `whitelist` on your AMP Instance via `Configuration -> Gameplay and Difficulty`
        - You must set the servers `//server server_name whitelist` to `true` to allow for users to request whitelist.
6. Once done; familarize yourself with the [**Commands**](COMMANDS.md)
---
## Features
- Multi-MC Server Support with Database integration for storing Server specific settings and controls!
- Expanding Support for plugins on your Minecraft Servers such as /tempban!
- **Auto-Reply** feature to assist players who are in need of information with customizable replies!
- **Spam Protection** on your Discord Server against Nitro bots and similar spam!
- **Auto-Whitelist** of Discord Users to your Minecraft Servers with a simple message.
- **Live** AMP Console to Discord Channels with ability to send server console commands.
- **Live** Minecraft Server Chat to Discord Channels with communication both ways.
- Resetting of the Ender Dragon Fight and World via Discord!
- Control over AMP Servers via Discord with commands such as Start, Stop, Kill and Restart. 
- Configurable Logging of all Discord Bot Commands and Server Commands by Users.
- Tracking of Discord Users Donator Status, Minecraft Playtime, In-Game Name, Last login, Infractions/Punishments, Whitelist status, Banned Status/Expiration Time and much more...
---
![img](img/gategif.gif)
---
**Version** alpha-1.0.1