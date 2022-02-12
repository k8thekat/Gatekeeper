# Sentinel Bot 
---
## About
I wanted to create a bot to handle whitelisting of minecraft servers from inside Discord and without any outside user interaction. Simply follow the whitelist format and the bot handles the rest. Then the project turned into what other functionality could I help a community with by allowing user documentation on subjects such as infractions, donations, Minecraft Name, Discord roles and punishments such as a temporary ban without someone having to keep track of when it expires. 

Some additional functionality was added for replying to players with certain keywords or allowing them to check the status of a server, allowing the AMP console to be output to a specific Discord channel, allowing Discord users to talk to players inside of a Minecraft server and allowing staff to control a server inside of Discord.

---
## Requirements

- Currently it is required that the user creates their own bot. 
    - See [Creating a bot Account](https://discordpy.readthedocs.io/en/stable/discord.html), when creating the bot set the **Bot Permissions Integer to: 2416249862.**
- Please Install [Python](https://www.python.org/); you will also need to install the required packages. 
    - **Run `pip install -r requirements.txt`** in the same directory as Sentinel Bot.
- You also need to be using [Cube Coders AMP](https://cubecoders.com/AMP) with a instance of Minecraft Java (any version later than 1.12) set up and running.

---

## Setup
1. Follow the instructions inside the `tokenstemplate.py file` and `config.py`
3. Run the script and wait for the Bot to connect.
4. Once the Bot has connected in any channel type `//setup discord_role_id` were `discord_role_id` is the master Operator/Owner of the Bot. 
    - See [Developer Mode](https://www.howtogeek.com/714348/how-to-enable-or-disable-developer-mode-on-discord/)
5. To see Bot errors, set up **Bot Settings: BotComms**
    - Use the command `//botsettings botcomms discord_channel_id` or `discord_channel_name` to set a channel for bot errors to be sent.
6. Setting up your AMP **Servers**
    - You must enable `whitelist` on your AMP Instance via `Configuration -> Gameplay and Difficulty`
        - You must set the servers `//server server_name whitelist` to `true` to allow for users to request whitelist.
---
