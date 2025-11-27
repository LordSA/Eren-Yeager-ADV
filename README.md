![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=WELCOME+TO+MY+DOMAIN!;MY+NAME+IS+EREN+YEAGER;I'M+A+POWERFUL+MOVIE+BOT;WITH+ULTRA+FEATURES!)
<p align="center">
  <img src="https://telegra.ph/file/7226c9d57dc698158bab2.jpg" alt="Eren Yeager Logo">
</p>

# 𝙴𝚁𝙴𝙽 𝚈𝙴𝙰𝙶𝙴𝚁 ADV5.2.0

[![Stars](https://img.shields.io/github/stars/LordSA/Eren-Yeager-ADV?style=flat-square&color=yellow)](https://github.com/LordSA/Eren-Yeager-ADV/stargazers)  
[![Forks](https://img.shields.io/github/forks/LordSA/Eren-Yeager-ADV?style=flat-square&color=orange)](https://github.com/LordSA/Eren-Yeager-ADV/fork)  
[![Size](https://img.shields.io/github/repo-size/LordSA/Eren-Yeager-ADV?style=flat-square&color=orange)](https://github.com/LordSA/Eren-Yeager-ADV/)  
[![Contributors](https://img.shields.io/github/contributors/LordSA/Eren-Yeager-ADV?style=flat-square&color=green)](https://github.com/LordSA/Eren-Yeager-ADV/graphs/contributors)  
[![License](https://img.shields.io/badge/License-AGPLv3-blue)](https://www.gnu.org/licenses/agpl-3.0.en.html)  

---

## 🚀 Features

* **Fully Asynchronous:** Built with `asyncio`, `Motor` (for MongoDB), and `AIOHTTP` to be extremely fast and non-blocking.
* **High-Performance Database:** Uses a single, indexed collection for files, and a modern schema for filters and users, allowing the bot to scale to millions of files without slowing down.
* **Auto Filter & Manual Filter**
* **IMDB Search & Info**
* **Advanced Admin Commands** (Ban, Broadcast, Stats, etc.)
* **Fast Inline Search**
* **Spell Check** (Finds movies even with typos)
* **Group Management** (Welcome, Admin Tools, Connections)
* **File Indexing** (Index all files from any channel)

---

## 🛠️ Environment Variables

Create a `.env` file in the root directory (or use an `ecosystem.config.js` file for PM2) and fill in these variables.

### Required Variables
| Variable | Description |
| :--- | :--- |
| `BOT_TOKEN` | Your bot token from [@BotFather](https://telegram.dog/BotFather). |
| `API_ID` | Your API ID from [my.telegram.org](https://my.telegram.org/apps). |
| `API_HASH` | Your API Hash from [my.telegram.org](https://my.telegram.org/apps). |
| `ADMINS` | A space-separated list of user IDs who will be bot admins. |
| `DATABASE_URI` | Your [MongoDB connection string](https://www.mongodb.com/basics/mongodb-connection-string) (e.g., `mongodb+srv://...`). |
| `DATABASE_NAME` | The name of your database (e.g., `ErenYeager`). |
| `LOG_CHANNEL` | A **private** channel/group ID (must start with `-100`) where the bot will send logs and new user alerts. |

### Optional Variables
| Variable | Description |
| :--- | :--- |
| `CHANNELS` | A space-separated list of channel/group IDs (e.g., `-100123... -100456...`) for the bot to **automatically index** new media from. |
| `AUTH_CHANNEL` | The ID of a channel/group that users **must** join to use the bot (Force Subscribe). |
| `SUPPORT_CHAT` | The username of your support group (e.g., `mwpro11`) used in help messages. |
| `PM2_BOT_NAME` | The **exact name** of your bot in PM2 (e.g., `eren-bot`). **Required for the `/update` command to work.** for vps hosters it is important |
| `P_TTI_SHOW_OFF` | `True` or `False`. If `True`, forces users to click a "Send to PM" button instead of receiving files in the group. |
| `SINGLE_BUTTON` | `True` or `False`. If `True`, filter results show as one button (`[File Name (Size)]`). If `False`, they show as two (`[File Name] [Size]`). |
| `PROTECT_CONTENT` | `True` or `False`. If `True`, all files sent by the bot will have "Forwarding" disabled. |
| `IMDB` | `True` or `False`. Set to `False` to disable all IMDB fetching. |
| `SPELL_CHECK_REPLY`| `True` or `False`. If `True`, the bot will suggest corrected spellings for failed searches. |
| `MELCOW_NEW_USERS` | `True` or `False`. Set to `True` to enable a welcome message for new users joining groups. |
| `CHPV` | Controls the media type on the `/start` command. Set to `pic` (default) or `vid`. |
| `PICS` | A space-separated list of Telegraph **photo** URLs for the `/start` command (used if `CHPV` is 'pic'). |
| `VIDS` | A space-separated list of Telegraph **video** URLs for the `/start` command (used if `CHPV` is 'vid'). |
| `CUSTOM_FILE_CAPTION` | A custom template for file captions. See `info.py` for an example. |
| `BATCH_FILE_CAPTION` | A custom template for batch file captions. See `info.py` for an example. |
| `IMDB_TEMPLATE` | A custom template for IMDB captions. See `info.py` for an example. |

---

## Deploy

<details><summary>Deploy To VPS</summary>
  
```bash
git clone https://github.com/LordSA/EREN-YEAGER-ADV5.2.0.git
cd /EREN-YEAGER-ADV5.2.0
python3 -m venv venv
source venv/bin/activate
```

# Install Packages
````
pip3 install U -r requirements.txt
````
Edit info.py with variables as given below then run bot(to test)
````
python3 bot.py
````
For Pm2 Deploying
````
python3 -m venv venv
source venv/bin/activate
pip3 install -U -r requirements.txt
sudo apt update && sudo apt install nodejs npm -y
sudo npm install pm2 -g

pm2 start venv/bin/python3 --name eren-bot -- bot.py
pm2 logs eren-bot
````
</details>

<details><summary>Deploy To Heroku</summary>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/LordSA/Eren-Yeager-ADV)
</details>

<details><summary>Deploy in Render</summary>

Preffered if you pay for it (i didn't tested in free version)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
</details>

## Commands

Here are the commands, separated by who can use them.

### 🤖 Bot Admin Commands
(Only for users listed in the `ADMINS` variable)

* `/logs` - Get the bot's log file.
* `/stats` - View bot statistics (total files, users, chats).
* `/users` - Get the list of all users in the database.
* `/chats` - Get the list of all groups in the database.
* `/broadcast` - Reply to a message to broadcast it to all users.
* `/index` - Reply to a message in a channel to index all its files.
* `/deleteall` - Deletes **all** indexed files from the database.
* `/checkupdate` - Check for new updates from the GitHub repo.
* `/update` - Update the bot to the latest version from GitHub (requires `PM2_BOT_NAME`).
* `/leave` - (Provide chat ID) Make the bot leave a group.
* `/disable` - (Provide chat ID) Disable a group.
* `/enable` - (Provide chat ID) Re-enable a group.
* `/ban` - (Reply or give ID) Ban a user from the bot.
* `/unban` - (Reply or give ID) Unban a user.
* `/channel` - Get a list of all indexed channels.

---

### 🧑‍⚖️ Group Admin Commands
(For group owners and admins)

* `/filter` - Add a manual filter.
* `/filters` - View all filters in the group.
* `/del` - Delete a specific filter.
* `/delall` - Delete all filters in the group.
* `/connect` - Connect your group to PM for managing filters.
* `/disconnect` - Disconnect your group from PM.
* `/connections` - View all your connected groups.
* `/settings` - Open the settings panel for your group.
* `/set_template` - Set a custom IMDB template for your group.
* `/pin` - Reply to a message to pin it.
* `/unpin` - Reply to a message to unpin it.
* `/purge` - Reply to a message to delete all messages up to it.
* `/inkick` - Kick inactive users (e.g., `/inkick recently`).
* `/dkick` - Kick deleted accounts.
* `/instatus` - View a group's user status (online, offline, etc.).

---

### 👤 User Commands
(For all users)

* `/start` - Check if the bot is alive and get the start menu.
* `/whois` - Reply to a user to get their info.
* `/id` - Get the chat ID or your user ID.
* `/imdb` - Search for movie/series info from IMDB.
* `/tgraph` - Reply to media (photo/video < 5MB) to get a Telegraph link.
* `/stickerid` - Reply to a sticker to get its ID.
* `/ping` - Check the bot's response speed.
* `/alive` - Check if the bot is alive (Malayalam).
* `/repo` - Get the bot's source code.

---

## Support
[![OWNER](https://img.shields.io/badge/Telegram-Group-30302f?style=flat&logo=telegram)](https://telegram.dog/shibili_offline)  
[![Telegram Channel](https://img.shields.io/badge/Telegram-Channel-30302f?style=flat&logo=telegram)](https://telegram.dog/mwpro11)

---

## Credits
- Dan — [Pyrogram Library](https://github.com/pyrogram/pyrogram)  
- Mahesh — [Media-Search-bot](https://github.com/Mahesh0253/Media-Search-bot)  
- Trojanz — [Unlimited Filter Bot](https://github.com/TroJanzHEX/Unlimited-Filter-Bot) & [AutoFilterBot](https://github.com/trojanzhex/auto-filter-bot)
- Subin for the Evamaria [Evamaria](https://github.com/EvamariaTG/Evamaria)  
- Everyone who supported this project

---

### Note
Forking, editing a few lines, or releasing a branch doesn’t make you the original developer. Fork the repo and edit as per your needs.

---

## Disclaimer
Licensed under [GNU AGPL v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html#header).  
Selling this code for money is *strictly prohibited*.
