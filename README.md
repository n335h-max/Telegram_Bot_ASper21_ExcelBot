# Telegram Notes Sharing Bot 📚

A simple Telegram bot for students to share and browse notes.

## Features
- **Upload Notes**: Students can share PDF files, images, or documents.
- **Title & Subject**: Each note is categorized by title and restricted to 5 core subjects.
- **Browse by Subject**: Students can easily find notes by their subject.
- **Search Notes**: Find notes instantly by searching for keywords in the title.
- **Manage Uploads**: Students can view and delete their own shared notes via a personal dashboard.
- **Easy Download**: Download notes directly from Telegram.

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher installed.
- A Telegram Bot token (already provided in `.env`).

### 2. Install Dependencies
Run the following command in your terminal:
```bash
pip install -r requirements.txt
```

### 3. Run the Bot
Start the bot by running:
```bash
python bot.py
```

## How to use
- `/start`: Welcome message and instructions.
- `/upload`: Start the note sharing process.
- `/browse`: View notes by subject.
- `/search [keyword]`: Find specific notes by title.
- `/my_notes`: View and delete your own uploads.
- `/help`: Get help with bot commands.

## Technical Details
- **Language**: Python
- **Library**: `python-telegram-bot`
- **Database**: SQLite (local file `notes_bot.db`)
- **Storage**: Uses Telegram's `file_id` system for efficient storage and retrieval.
