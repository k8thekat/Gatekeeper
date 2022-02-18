# Gatekeeper Bot - Commands
___

## Setup

1. Setting up **Server Commands: DiscordChannel** 
    - Set a Discord Console Channel if you want the AMP console output to that channel. 
        - You must set `//botsettings autoconsole true` for the console to go live. <br>
    - Set a Discord Chat channel if you want to be able to talk and see in game chat in Discord. <br>
2. Setting up **Bot Commands: Whitelist**
    - Set a Discord channel for the bot to read messages for whitelist requests via `//botsettings whitelist (discord_channel_id` or `discord_channel_name)`
    - This allows the bot to store the users `discord_name`, `discord_user_id` and their `minecraft_ign` to a database. 
        - If **Bot Settings: AutoWhitelist** is `TRUE` then the bot will whitelist that user's `minecracft_ign` to the specified `server_name`
    - Format for whitelist requests is: **`IGN: minecraft_ign SERVER: (server_name` or `server_nickname)`**
3. Setting up **Role Commands: Permissions**
    - Set a Discord Roles permissions via `//role (discord_role_id` or `discord_role_name) set (role) (true` or `false)`
    - Almost all commands require a certain permission, a role can have more than one permission set to `true`

---
---
## Command Usage
All commands can be used in any channel the bot can see. They are not case sensitive! <br>
**Commands are triggered via two forward slashes. `//`**. 
- You can use `//help` at any time for commands. 
    - Some Commands support `list` and `info` after any Command and or its function, the bot will reply with information.
- All `time` parameters support values: `Years(y:) Months(mo:) Weeks(w:) Days(d:) Hours(h:) Minutes(m:) Seconds(s:)` 
    - All `time` parameters are optional. *example: `//server server_name userban user_name y:2d:4m:45`*
- When removing infractions; no `time` or `reason:` needs to be specified. Use `//user info` to get the `InfractionID`.
    - *example: `//user user_name infractions del 1`*
- All `user_name` entires support parameters: `discord_user_id` or `discord_user_name` or `minecraft_ign` <br>
- All `channel` entires support parameters: `discord_channel_id` or `discord_channel_name` <br>
- All `role` entries support parameters: `discord_role_id` or `discord_role_name`
- All `server_name` entries support parameters: `server_nicknames` too. See **Global Commands: Serverlist**<br>
---
### Global Commands
*example: `//rolelistperms Maintenance`* | *example 2: `//banhammer discord_user_id or discord_name`*
- **Pardon** | Permission level: infraction | Usage: Un-bans a user from Discord and all AMP servers. <br>
- **Banhammer** | Permission level: infraction | Usage: Permenatly bans a user from the Discord and all AMP servers. <br>
- **Serverlist** | Permission level: info | Usage: Returns a list of all Servers that AMP has that are running along with Server nicknames. <br>

---
### Server Commands `//server` 
*example: `//server server_name discordchannel chat (discord_id` or `discord_channel_name)`* <br>
- **Channel** | *default: None* | options: `chat` or `console` | parameters: `channel` Permission level: `Maintenance` | <br>
- **Donator** | *default: False* | parameters: `true` or `false` | Permission level: `Maintenance` |  <br>
- **Info** | *No Options or Parameters* | Permission level: `General` | <br>
- **Kill** | *No Options or Parameters* | Permission level: `Maintenance` |<br>
- **Maintenance** | *default: off* | parameters: `on` or `off` | Permission level: `Maintenance` |<br>
- **Nickname** | *default: None* | options: `list` or `add` or `remove` | Permission level: `Maintenance` | <br>
- **Restart** | *No Options or Parameters* | Permissions level: `Maintenance` | <br>
- **Role** | *default: None* | parameters: `role` | Permission level: `Maintenance` |  <br>
- **Start** | *No Options or Parameters* | Permission level: `Maintenance` | <br>
- **Status** | *No Options or Parameters* | Permission level: `None` | <br>
- **Stop** | *No Options or Parameters* | Permission level: `Maintenance` | <br>
- **UserBan** | *No Options* | parameters: `user_name` / `time(optional)` / `reason:(optional)` | Permission level: `Staff` | <br>
- **UserInfractions** | *No Options* | parameters: `user_name` / `note(optional)` | Permission level: `Staff` |  <br>
- **UserList** | *No Options or Parameters* | Permission level: `Staff` | <br>
- **Whitelist** | *default: False* | parameters: `true` or `false` | Permission level: `Maintenance` |<br>

---
### Role Commands `//role`
*example: `//role discord_role_id set Staff (true` or `false)`*
- **Set** | *No Options* | parameters: `role` / `role_name` /  Permission level: `Admin` <br>

### Role Rank
These ranks do follow a heirachy starting from `General` to `Operator`; each rank can only have one `discord role` per. Set them via the `//role discord_role_id set (rank)`<br>
- **Operator** | Full control over the bot, this is set during startup.
- **Admin**  | Similar to Operator, Full Control over the bot.
- **Maintenance**  | Full access to Bot commands/settings, AMP commands/settings and Console.
- **Moderator**  | Full access to Bot commands/settings.
- **Staff**  | Full access to User commands and Ban/Pardon.
- **General** | Basic User with access to Server Chat, Server List
---
### User Commands `//user`
*example: `//user discord_id donator (true` or `false`)* 
- **Add** | *No Options* | parameters: `user_name` | Permission level: `Staff` <br>
- **Ban** | *No Options* | parameters: `user_name` / `time(optional)` / `reason:(optional)` | Permisson level: `Staff` <br>
- **Donator** | *No Options* | parameters: `user_name` `true` or `false` | Permission level: `Moderator` <br>
- **IGN** | *No Options* | parameters: `user_name` | Permission level: `Staff` <br>
- **Info** | *No Options* | parameters: `user_name` | Permission level: `Staff` <br>
- **Infractions** | options: `add` or `del` | parameters: `user_name` / `infractionID(del:optional)` / `time(add:optional)` / `reason:(add:optional)` | Permission level: `Staff` <br>
- **Moderator** | *No Options* | parameters: `user_name` / `true` or `false` | Permission level: `Maintenance` <br>
---
### Bot Commands `//botsettings`
*example: `//botsetting autowhitelist (true` or `false)`* |  *example 2: `//botsetting infractiontimeout time`*</br>
 **All Bot Settings require Permission level: `Moderator` or higher**</br>

#### ***Flags*** | *default: False*
- **AutoConsole** | parameters: `true` or `false` | Usage: Allows Server console to be output to predefined channels per Server (See Server Functions -> DiscordChannel)
- **Autowhitelist** | parameters: `true` or `false` | Usage: Allows the bot to whitelist the User for the specified Server
- **Autorole** | parameters: `true` or `false`| Usage: Allows the bot to set the Users role to the Server defined Role in Discord (See Server Functions -> Role)
- **Autoreply** | parameters: `true` or `false`| Usage: Allows the bot to reply to predefined strings (help,server version,ip)
- **ConvertIGN** | Usage: Converts chat names from Discord to IGN when talking in a Minecraft Servers Chat

#### ***Channel*** | *default: None*
- **Whitelistchannel** | Usage: Sets the whitelist channel the bot will read messages in for auto-whitelist functionality.
- **FAQchannel** | Usage: Provides a channel link in bot replies to point to a FAQ channel or something similar of your discord server.
- **Supportchannel** | Usage: Provides a channel link in bot replies to point to a Support channel or something similar of your discord server.
- **Ruleschannel** | Usage: Provides a channel link in bot replies to point to a Rules channel or something similar of your discord server.
- **Infochannel** | Usage: Provides a channel link in bot replies to point to a Info channel or something similar of your discord server.
- **Botcomms** | Usage: Any errors the bot encounters will be output to this channel.
        
#### ***Time*** | See `time`
- **Infractiontimeout** | *default: expire in 2 weeks*
- **Bantimeout** | *default: expire in 3 days*
- **WhitelistWaitTime** | *default: 0* | Usage: Delays the whitelist request for a specified number of minutes.

---
### Log Commands `//log`
- Currently all log files are local and can be accessed in the same directory as the bot `Gatekeeper/logs`<br>
- **List** | Usage: Lists all files in the `Gatekeeper/logs` folder
- **Read** | Usage: Read entries from a specific log file.