# Discord XP Bot

[![Python](https://img.shields.io/badge/Python-000000?style=flat&logo=python)](https://www.python.org) [![Discord.py](https://img.shields.io/badge/Discord.py-000000?style=flat&logo=discord)](https://discordpy.readthedocs.io/en/latest/) [![Status](https://img.shields.io/badge/Status-Completed-blue?style=flat)](https://github.com/Botnikkk/XP-BOT)

A simple yet powerful XP bot for Discord servers designed to encourage user activity and engagement through a customizable leveling system.

## ✨ Features

* **XP & Leveling:** Automatically tracks user messages and rewards them with experience points.
* **Leaderboards:** A server-wide leaderboard to foster friendly competition.
* **Role Rewards:** Automatically assign roles to users when they reach a specific level or rank.
* **Admin Control:** Admins can manually adjust user XP, set levels, and reset data.
* **Customization:**
    * Designate "spam" channels where no XP can be earned.
    * Blacklist specific roles from gaining XP.
    * Set a dedicated channel for level-up announcement messages.

---

## 🤖 Bot Commands

All commands are prefixed with `n?`.

### **`help`**
Displays the list of available commands.
```bash
n?help
```

### **`rank`**
Checks the current level, rank, and XP of a user.
```bash
n?rank @{user}
```
* `@{user}` (Optional): The user whose rank you want to see. If left blank, it will show your own rank.

### **`leaderboard`**
Displays the server's top 10 users with the most XP.
```bash
n?leaderboard
```

### **`set_levelrole`**
Assigns a role to be automatically given when a user reaches a specific level.
```bash
n?set_levelrole @{role} {level}
```
* `@{role}` (Required): The role to be awarded.
* `{level}` (Required): The level required to receive the role.

### **`set_rankrole`**
Assigns a role to be automatically given when a user reaches a specific rank on the leaderboard.
```bash
n?set_rankrole @{role} {rank}
```
* `@{role}` (Required): The role to be awarded.
* `{rank}` (Required): The leaderboard rank required to receive the role.

### **`set_noxp`**
Blacklists a role from earning any XP.
```bash
n?set_noxp @{role}
```
* `@{role}` (Required): The role to be blacklisted.

### **`set_levelchannel`**
Sets a specific channel where all "level up" messages will be sent.
```bash
n?set_levelchannel #{channel}
```
* `#{channel}` (Required): The channel for level-up announcements.

### **`set_spamchannel`**
Disables XP gain in a specific channel.
```bash
n?set_spamchannel #{channel}
```
* `#{channel}` (Required): The channel to be marked as no-XP.

### **`givexp`**
Manually gives a specified amount of XP to a user.
```bash
n?givexp @{user} {amount}
```
* `@{user}` (Required): The user to receive XP.
* `{amount}` (Required): The amount of XP to give.

### **`setlevel`**
Manually sets a user to a specific level.
```bash
n?setlevel @{user} {level}
```
* `@{user}` (Required): The user whose level is being changed.
* `{level}` (Required): The level to set them to.

### **`resetxp`**
Resets all XP and level data for a specific user.
```bash
n?resetxp @{user}
```
* `@{user}` (Required): The user whose data will be reset.

---

## 🛠️ Tech Stack

* **Languages:** **Python**, **SQL**
* **Libraries:** **Discord.py**, **Asyncio**, **Dotenv**

---

## 📧 Contact

Nikhil Chaudhary - [@botnikkk](https://www.linkedin.com/in/botnikkk) - b.nikk.chd@gmail.com

Project Link: [https://github.com/Botnikkk/XP-BOT](https://github.com/Botnikkk/XP-BOT)