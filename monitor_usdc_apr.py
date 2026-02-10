import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Configuration
AAVESCAN_URL = "https://aavescan.com/ethereum-v3/usdc"
STATE_FILE = "last_apr.json"
THRESHOLD = 0.01  # Alert if change is greater than 0.01% (adjust as needed)

# Notification settings - choose your method
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

def get_usdc_supply_apr():
    """Scrape the USDC supply APR from Aavescan"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(AAVESCAN_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the supply APR - this may need adjustment based on actual HTML structure
        # Look for the supply APR percentage on the page
        # This is a simplified example - you might need to inspect the actual page
        
        # Method 1: Try to find it in the page text
        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            if 'Supply APR' in line or 'supply APR' in line:
                # The APR might be in the next line or same line
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if '%' in lines[j]:
                        apr_text = lines[j].replace('%', '').strip()
                        try:
                            apr = float(apr_text)
                            return apr
                        except ValueError:
                            continue
        
        # Method 2: Look for specific table or div structure
        # You may need to inspect the actual HTML and adjust this
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for i, cell in enumerate(cells):
                    if 'Supply APR' in cell.get_text():
                        if i + 1 < len(cells):
                            apr_text = cells[i + 1].get_text().replace('%', '').strip()
                            try:
                                return float(apr_text)
                            except ValueError:
                                continue
        
        print("Could not find Supply APR on the page")
        return None
        
    except Exception as e:
        print(f"Error fetching APR: {e}")
        return None

def load_last_state():
    """Load the last recorded APR from file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('apr'), data.get('timestamp')
        except Exception as e:
            print(f"Error loading state: {e}")
    return None, None

def save_state(apr):
    """Save the current APR to file"""
    try:
        data = {
            'apr': apr,
            'timestamp': datetime.now().isoformat()
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def send_discord_notification(old_apr, new_apr, change):
    """Send notification via Discord webhook"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        emoji = "📈" if change > 0 else "📉"
        color = 0x00ff00 if change > 0 else 0xff0000
        
        payload = {
            "embeds": [{
                "title": f"{emoji} USDC Supply APR Changed on Aave",
                "description": f"The supply APR has changed from **{old_apr}%** to **{new_apr}%**",
                "color": color,
                "fields": [
                    {
                        "name": "Change",
                        "value": f"{change:+.4f}%",
                        "inline": True
                    },
                    {
                        "name": "New APR",
                        "value": f"{new_apr}%",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"Checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                },
                "url": "https://aavescan.com/ethereum-v3/usdc"
            }]
        }
        
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        response.raise_for_status()
        print("Discord notification sent successfully")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def send_telegram_notification(old_apr, new_apr, change):
    """Send notification via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    try:
        emoji = "📈" if change > 0 else "📉"
        message = f"""{emoji} *USDC Supply APR Changed*

Old APR: `{old_apr}%`
New APR: `{new_apr}%`
Change: `{change:+.4f}%`

[View on Aavescan](https://aavescan.com/ethereum-v3/usdc)
"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram notification sent successfully")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

def send_notifications(old_apr, new_apr):
    """Send all configured notifications"""
    change = new_apr - old_apr
    
    print(f"\n{'='*50}")
    print(f"APR CHANGE DETECTED!")
    print(f"Old APR: {old_apr}%")
    print(f"New APR: {new_apr}%")
    print(f"Change: {change:+.4f}%")
    print(f"{'='*50}\n")
    
    send_discord_notification(old_apr, new_apr, change)
    send_telegram_notification(old_apr, new_apr, change)

def main():
    print(f"Starting USDC APR monitor - {datetime.now().isoformat()}")
    
    # Get current APR
    current_apr = get_usdc_supply_apr()
    
    if current_apr is None:
        print("Failed to fetch current APR")
        return
    
    print(f"Current USDC Supply APR: {current_apr}%")
    
    # Load last known APR
    last_apr, last_timestamp = load_last_state()
    
    if last_apr is None:
        print("First run - saving initial state")
        save_state(current_apr)
        return
    
    print(f"Last recorded APR: {last_apr}% (at {last_timestamp})")
    
    # Check if APR has changed significantly
    change = abs(current_apr - last_apr)
    
    if change >= THRESHOLD:
        send_notifications(last_apr, current_apr)
        save_state(current_apr)
    else:
        print(f"APR change ({change:.4f}%) is below threshold ({THRESHOLD}%)")
        # Still update the state with current value and timestamp
        save_state(current_apr)

if __name__ == "__main__":
    main()
