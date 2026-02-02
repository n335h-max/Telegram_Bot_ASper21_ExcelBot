# Deploying to Render.com ☁️

Render is a modern cloud provider. The free tier works well, but it "spins down" (sleeps) after 15 minutes of inactivity. To prevent this, we've added a special "keep-alive" web server to your bot.

## Step 1: Upload Code to GitHub
Render pulls code from GitHub, so you need to push your project there first.
1. Create a new repository on [GitHub](https://github.com).
2. Upload all your project files (`bot.py`, `database.py`, `keep_alive.py`, `requirements.txt`).
   *(Do NOT upload `.env`! You will set environment variables directly in Render).*

## Step 2: Create a Web Service on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/) and log in.
2. Click **"New +"** and select **"Web Service"**.
3. Connect your GitHub repository.
4. **Configure the Service:**
   - **Name**: `asper21-bot` (or anything you like)
   - **Region**: Closest to you (e.g., Singapore, Oregon)
   - **Branch**: `main` (or `master`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: `Free`

## Step 3: Add Environment Variables
1. Scroll down to the **"Environment Variables"** section.
2. Add the following keys and values (copy from your `.env` file):
   - Key: `TELEGRAM_BOT_TOKEN` | Value: `Your_Token_Here`
   - Key: `ADMIN_ID`           | Value: `Your_ID_Here`

## Step 4: Deploy & Keep Alive
1. Click **"Create Web Service"**.
2. Render will build your bot. Wait for it to finish.
3. Once deployed, you will see a URL like `https://asper21-bot.onrender.com` at the top.
4. **Important**: Because this is a free "Web Service", Render will put it to sleep if nobody visits that URL.
5. **The Fix**: Create a free account at [UptimeRobot](https://uptimerobot.com/).
   - Click "Add New Monitor".
   - Type: `HTTP(s)`
   - Friendly Name: `My Bot`
   - URL: `https://asper21-bot.onrender.com` (Your Render URL)
   - Monitoring Interval: `5 minutes`
   - Click "Create Monitor".

**Done!** UptimeRobot will ping your bot every 5 minutes, keeping it awake 24/7 on Render's free tier. 🚀
