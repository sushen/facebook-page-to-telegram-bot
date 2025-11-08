# Facebook → Telegram Responder

When someone sends a message to your **Facebook Page**, this small Flask app
forwards the message to your **Telegram chat or channel**.

## 🧠 How it works
1. Set up a Facebook App & Webhook to receive messages.
2. The Flask server receives new messages from Facebook.
3. The app sends a notification to your Telegram bot using `requests`.

## 🧰 Environment Variables
| Name | Description |
|------|--------------|
| `FB_VERIFY_TOKEN` | Token used for Facebook webhook verification |
| `FB_PAGE_ACCESS_TOKEN` | Your Facebook page access token |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | Chat ID where messages will be sent |

## 🧑‍💻 Deployment
This can run for free on **Render**, **Railway**, or **Fly.io**.

Example Render command:
```bash
gunicorn app:app
