# Facebook → Telegram Responder

When someone sends a message to your **Facebook Page**, this small Flask app
forwards the message to your **Telegram chat or channel**.

## 🧠 How it works
1. Set up a Facebook App & Webhook to receive messages.
2. The Flask server receives new messages from Facebook.
3. The app sends a notification to your Telegram bot using `requests`.

## 🧰 Environment Variables
| Name | Description |
|------|-------------|
| `FB_VERIFY_TOKEN` | Token used for Facebook webhook verification |
| `FB_PAGE_ACCESS_TOKEN` | *(Optional)* Facebook page access token |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `TELEGRAM_CHAT_ID` | Chat ID where messages will be sent |
| `TELEGRAM_PARSE_MODE` | Optional parse mode (`MarkdownV2`, `HTML`, …) |
| `TELEGRAM_DISABLE_NOTIFICATIONS` | Set to `true` to silence notifications |
| `LOG_LEVEL` | Optional logging level (defaults to `INFO`) |

Create a `.env` file with these values so the application can load them
automatically via [`python-dotenv`](https://github.com/theskumar/python-dotenv).

```
FB_VERIFY_TOKEN=super-secret
FB_PAGE_ACCESS_TOKEN=EAAP...
TELEGRAM_BOT_TOKEN=123456:ABC
TELEGRAM_CHAT_ID=987654321
```

## 🚀 Running locally
1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Start the development server
   ```bash
   flask --app app run --reload
   ```
3. Expose port `5000` to Facebook using a tunnelling service such as
   [`ngrok`](https://ngrok.com/) or [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/).
4. Configure the Facebook webhook callback to `https://<your-tunnel>/webhook` and
   use the same `FB_VERIFY_TOKEN` as above.

You can check the health endpoint at `GET /` and the verification endpoint at
`GET /webhook` using your browser or `curl`.

### ✅ Running tests
Install the development dependencies and execute `pytest`:

```bash
pip install -r dev-requirements.txt
pytest
```

## 📦 Deploying
The repository includes a `Procfile` compatible with Render/Railway/Heroku-style
platforms:

```
web: gunicorn app:application
```

Set the environment variables in your hosting provider and you are ready to go.

### 🚀 Deploying to Fly.io

This repository already includes the required deployment files for Fly.io:

- `fly.toml` – application configuration with the HTTP service exposed on port `8000`.
- `Dockerfile` – builds the production image with Gunicorn listening on `0.0.0.0:8000`.

To deploy:

1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/).
2. Authenticate and create your app: `fly auth login` and `fly launch --no-deploy --copy-config` (this reuses the checked-in `fly.toml`).
3. Deploy the application: `fly deploy`.

Fly will automatically provision the environment variables defined in `fly.toml`. Make
sure to set the required secrets using `fly secrets set <KEY>=<VALUE>` before
deploying.

