# Bot
Telegram_Movie_Downloader
{
  "builds": [
    {
      "src": "api/webhook.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/webhook",
      "dest": "api/webhook.py"
    }
  ]
}
