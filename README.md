# USDC APR Monitor for Aave

Automatically monitors the USDC supply APR on Aave (via Aavescan) and sends notifications when it changes.

## How It Works

1. **Runs automatically** every 15 minutes using GitHub Actions (free!)
2. **Remembers the last value** by storing it in `last_apr.json` in the repository
3. **Sends notifications** via Discord or Telegram when the APR changes

## Setup Instructions

### 1. Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new **public** repository (free unlimited actions)
3. Name it something like `usdc-apr-monitor`

### 2. Upload These Files

Upload all these files to your repository:
- `monitor_usdc_apr.py` - The main monitoring script
- `.github/workflows/monitor_apr.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies
- `README.md` - This file

### 3. Set Up Notifications

Choose one or both notification methods:

#### Option A: Discord Webhook

1. In your Discord server, go to **Server Settings → Integrations → Webhooks**
2. Click **New Webhook**
3. Name it "USDC APR Monitor" and choose a channel
4. Copy the webhook URL
5. In your GitHub repo, go to **Settings → Secrets and variables → Actions**
6. Click **New repository secret**
7. Name: `DISCORD_WEBHOOK_URL`
8. Value: Paste your webhook URL
9. Click **Add secret**

#### Option B: Telegram Bot

1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token
4. Start a chat with your bot and send any message
5. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
6. Find your `chat_id` in the response
7. In GitHub repo **Settings → Secrets and variables → Actions**, add:
   - `TELEGRAM_BOT_TOKEN` - Your bot token
   - `TELEGRAM_CHAT_ID` - Your chat ID

### 4. Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The monitor will now run every 15 minutes automatically!

### 5. Test It

1. Go to **Actions** tab
2. Click on **Monitor USDC APR** workflow
3. Click **Run workflow** button to test it manually
4. Watch the logs to see if it works

## Configuration

Edit `monitor_usdc_apr.py` to customize:

```python
# Change how often to check (in the .github/workflows/monitor_apr.yml file)
# Current: every 15 minutes
# Options: */5 (every 5 min), */30 (every 30 min), 0 * (every hour)

# Change the alert threshold (currently 0.01%)
THRESHOLD = 0.01  # Only alert if APR changes by more than this amount
```

## How the State is Stored

The script stores the last known APR in `last_apr.json`:

```json
{
  "apr": 2.22,
  "timestamp": "2024-02-10T15:30:00"
}
```

This file is automatically committed back to the repository after each check, so GitHub Actions always has the latest value to compare against.

## Schedule Options

Edit `.github/workflows/monitor_apr.yml` to change frequency:

```yaml
schedule:
  - cron: '*/5 * * * *'   # Every 5 minutes (GitHub minimum)
  - cron: '*/15 * * * *'  # Every 15 minutes (recommended)
  - cron: '*/30 * * * *'  # Every 30 minutes
  - cron: '0 * * * *'     # Every hour
  - cron: '0 */6 * * *'   # Every 6 hours
```

## Troubleshooting

### Monitor not running?
- Check the **Actions** tab for any errors
- Make sure the repository is **public** (private repos have limited free Actions minutes)
- Verify GitHub Actions is enabled in repository settings

### Not receiving notifications?
- Check the Actions logs for error messages
- Verify your webhook URL or bot token is correct
- Test your Discord webhook with a curl command
- Make sure your Telegram bot has permission to message you

### APR not detected?
- The website structure might have changed
- Check the Actions logs to see what the script is finding
- You may need to update the parsing logic in `get_usdc_supply_apr()`

## Alternative: Run Locally

If you prefer to run this on your own computer:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DISCORD_WEBHOOK_URL="your_webhook_url"
# or
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Run once
python monitor_usdc_apr.py

# Or run continuously (checks every 5 minutes)
while true; do python monitor_usdc_apr.py; sleep 300; done
```

## Cost

**GitHub Actions:** FREE
- Public repos get unlimited minutes
- Private repos get 2,000 free minutes/month

This monitor uses about 1 minute per check, so even running every 5 minutes would be ~8,640 minutes/month. Use a public repo to stay free!

## License

MIT License - Feel free to modify and use as needed!
