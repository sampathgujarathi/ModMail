# Discord Modmail Bot

A Discord Modmail Bot is a powerful tool that allows server members to contact the server moderators/administrators privately, creating a streamlined and efficient system for handling user inquiries, reports, and other communication.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)

## Features

- Allows users to contact server moderators/administrators privately.
- Simplifies the process of handling and responding to user inquiries, reports, and other communication.
- Provides a user-friendly and efficient way to manage and track conversations.

## Requirements

To run the Discord Modmail Bot, you will need the following:

- Python 3.8 or higher installed on your machine.
- Discord bot token. You can create a bot and obtain its token by creating a new application on the [Discord Developer Portal](https://discord.com/developers/applications).

## Installation

1. Clone or download the repository to your local machine.
2. Open a terminal or command prompt and navigate to the project directory.
3. Install the required dependencies by running the following command:

```python
   pip install -r requirements.txt
```
4. Run bot by following command:
```python
    py main.py
```

## Configuration
1. Open `config.py` and add your bot token, guild_id where bot is gonna used, ticket_channel_id the channel where you want to get tickets
2. You can run the bot now