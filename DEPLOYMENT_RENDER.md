# Deploying to Render.com (Webhook Mode) 🚀

This guide sets up your bot using **Webhooks**. This is better than Polling for Render because:
1. It solves the "Conflict" errors.
2. It wakes up your bot automatically when a message arrives (no need for UptimeRobot!).
3. It's more stable.

## Step 1: Push Code to GitHub
1. Open your terminal in this project.
2. Run these commands to update your code on GitHub:
   ```bash
   git add .
   git commit -m "Switch to Webhook mode"
   git push
   ```

## Step 2: Configure Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Select your `asper21-bot` service.
3. Go to **Settings**.
4. Scroll to **Environment Variables**.
5. Add a new variable:
   - **Key**: `WEBHOOK_URL`
   - **Value**: `https://your-service-name.onrender.com`
   *(Copy this URL from the top of your Render dashboard. Do NOT include a trailing slash `/`)*.

## Step 3: Deploy
1. Click **Manual Deploy** -> **Deploy latest commit**.
2. Wait for it to finish.
3. Your bot is now live!

## Troubleshooting

### "RuntimeError: To use start_webhook..."
If you see this error, it means Render is using an old version of the dependencies.
1. Go to your Service in Render.
2. Click **Manual Deploy** -> **Clear Build Cache & Deploy**.
3. This forces Render to re-install all libraries (including the missing `tornado`).

### "Conflict: terminated by other getUpdates request"
This means you are still running the bot locally OR Polling mode is still active.
- Ensure `WEBHOOK_URL` is set in Environment Variables.
- Stop any local instances of the bot.

## How it works
- When you set `WEBHOOK_URL`, the bot starts a web server listening on port 8080 (or whatever Render assigns).
- It tells Telegram: "Send all messages to `https://your-app.onrender.com/YOUR_TOKEN`".
- Telegram pushes messages to your bot.
- If the bot is sleeping, Render wakes it up instantly.
