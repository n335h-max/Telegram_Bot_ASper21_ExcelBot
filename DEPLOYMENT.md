# Deploying ASper21_ExcelBot to PythonAnywhere ☁️

This guide will help you host your bot on **PythonAnywhere** so it runs online.

## Option 1: The "Free Tier" Method (Good for Testing)
*Note: The free tier is great for testing, but you cannot run a "Polling" bot (like this one) 24/7 forever. It may stop if the console is closed or inactive for too long. For permanent 24/7 hosting, you need the $5/month "Hacker" plan or use a different method.*

### Step 1: Create an Account
1. Go to [www.pythonanywhere.com](https://www.pythonanywhere.com/) and sign up for a **Beginner** (Free) account.

### Step 2: Upload Your Code
1. Log in to your Dashboard.
2. Click on the **"Files"** tab (top right).
3. In the "Directories" sidebar on the left, type `TelegramBot` and click **"New directory"**.
4. Click into that new `TelegramBot` folder.
5. Upload the following files from your computer (use the "Upload a file" button):
   - `bot.py`
   - `database.py`
   - `requirements.txt`
   - `.env` (Make sure this has your real Token and Admin ID!)

### Step 3: Install Dependencies
1. Click on the **"Consoles"** tab (top right).
2. Under "Start a new console:", click **"Bash"**.
3. A terminal window will open. Type these commands (press Enter after each):

```bash
cd TelegramBot
pip install --user -r requirements.txt
```

### Step 4: Run the Bot
1. Still in the Bash console, run:
```bash
python bot.py
```
2. You should see "Bot is starting...". Your bot is now online! 
3. **Keep this browser tab open** to keep the bot running.

---

## Option 2: The "Always-On" Method (Recommended for 24/7)
*Requires a $5/month Paid Account.*

1. **Upgrade** your account to the "Hacker" plan ($5/mo).
2. Follow **Steps 2 & 3** above to upload files and install dependencies.
3. Go to the **"Tasks"** tab on your Dashboard.
4. Under "Always-on tasks", enter the command:
   ```bash
   python3.10 /home/yourusername/TelegramBot/bot.py
   ```
   *(Replace `yourusername` with your actual PythonAnywhere username)*.
5. Click **Create**.
6. PythonAnywhere will now restart your bot automatically if it crashes or the server restarts. It runs 24/7!

---

## Troubleshooting
- **Error: `Address already in use`**: This means an old version of your bot is still running. Go to the "Consoles" tab and kill any old consoles, or use `killall python` in the Bash console.
- **Bot stops responding**: On the free tier, this happens if you close the browser or after a set time. Restart it by opening a new Bash console and running `python bot.py` again.
