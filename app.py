import os
import credentials
from slack_bolt import App
from crawlpage import GetDate, GetToday, prettyPrint

# Initializes your app with your bot token and signing secret
app = App(
    token=credentials.SLACK_BOT_TOKEN,
    signing_secret=credentials.SLACK_SIGNING_SECRET
)

# Start your app
if __name__ == "__main__":
    try:
        # Create app instance
        app.start(port=int(os.environ.get("PORT", 63000)))
        
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("[Crtl+C] Shutting down.")
