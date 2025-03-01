![Static Badge](https://img.shields.io/badge/build-completed-brightgreen)

![Static Badge](https://img.shields.io/badge/status-online-brightgreen)

# Discord XP BOT



A simple XP-based discord bot.
## Features

- Message tracking and XP rewards.
- Role assignment based on level.
- Role assignment based on rank.
- Server leaderboard display.
- No XP for spam channel.
- Blacklist users from earning XP.
- Admin edits user XP levels.

## Commands

#### Help

```http
  n?help
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `None`    | `NA` | `NA`|

#### View rank

```http
  n?rank @{user}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user`      | `string` | **Optional**. Username of the user to be viewed |

#### View leaderboard

```http
  n?leaderboard 
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `None`      | `NA` | `NA` |

#### Set a role for a level

```http
  n?set_levelrole @{role} {level}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `role`      | `string` | **required**. Role being assigned to the level |
| `level`      | `integer` | **required**. Level to which the role is being assigned|

#### Set a role for a rank

```http
  n?set_levelrole @{role} {rank}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `role`      | `string` | **required**. Role being assigned to the level |
| `rank`      | `integer` | **required**. Rank to which the role is being assigned|

#### Set a role for xp blacklist

```http
  n?set_noxp @{role}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `role`      | `string` | **required**. Role to be blocked from gaining experience points |

#### Set a channel for level up messages

```http
  n?set_levelchannel #{channel}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `channel`      | `string` | **required**. Channel to set for level up messages |

#### Set a channel with no xp

```http
  n?set_spamchannel #{channel}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `channel`      | `string` | **required**. Channel to set as no xp channel |


#### Give a user xp

```http
  n?givexp @{user} {ammount}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user`      | `string` | **required**. User whom the xp is being given to |
| `ammount`      | `integer` | **required**. Ammount of xp to be given|

#### Give a user xp

```http
  n?setlevel @{user} {level}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user`      | `string` | **required**. User whose level is to be changed |
| `level`      | `integer` | **required**. Level to be set|

#### Reset data of a user

```http
  n?resetxp @{user}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user`      | `string` | **required**. User for whom xp is to be reseted |

## Tech Stack

**languages:** Python, SQL

**Libraries:** Discord.py, Asyncio, Dotenv


## Authors

- [@Botnikkk](https://www.github.com/Botnikkk)

