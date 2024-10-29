import asyncio
import os
from datetime import datetime
import discord
import requests
import pytz

# Discord bot token
my_secret = os.environ['TOKEN']

# Set up Discord bot intents and client
intents = discord.Intents.all()
client = discord.Client(intents=intents)
CHANNEL_ID = 1300557774165512205

DODGERS_ID = 119 
last_sent_date = None  # Variable to store the date of the last message sent

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        print("Bot ready and monitoring for Dodgers wins.")
        # Start checking game results in a loop
        client.loop.create_task(check_for_dodgers_win(channel))

async def check_for_dodgers_win(channel):
    global last_sent_date  # Use the global variable to track the last sent date
    while True:  # Ensures continuous checking
        try:
            # Get the current date in your local timezone (adjust as needed)
            timezone = pytz.timezone("America/Los_Angeles")  # Replace with your timezone
            today = datetime.now(timezone).strftime("%m/%d/%Y")
            ESPN_URL = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&teamId={DODGERS_ID}"

            # Fetch data from the API
            response = requests.get(ESPN_URL)
            data = response.json()

            # Check if there are any games
            if data["totalGames"] > 0:
                game = data["dates"][0]["games"][0]
                home_team = game["teams"]["home"]
                away_team = game["teams"]["away"]

                # Check if the Dodgers won
                if (home_team["team"]["id"] == DODGERS_ID and home_team["isWinner"]) or \
                   (away_team["team"]["id"] == DODGERS_ID and away_team["isWinner"]):

                    # Check if the message has already been sent today
                    if last_sent_date != today:
                        # Update the last sent date to today
                        last_sent_date = today

                        # Send the winning message
                        if home_team["team"]["id"] == DODGERS_ID:
                            score_message = f"The Dodgers won the game against the {away_team['team']['name']}! Score: {home_team['score']} - {away_team['score']} FREE CHICK FIL A SANDWICH"
                        else:
                            score_message = f"The Dodgers won the game against the {home_team['team']['name']}! Score: {away_team['score']} - {home_team['score']} FREE CHICK FIL A SANDWICH"

                        await channel.send(score_message)
                    else:
                        print("Message already sent today.")
                else:
                    print("No wins for the Dodgers today.")
            else:
                print("No games today for the Dodgers.")
        except Exception as e:
            print(f"Error fetching game data: {e}")

        await asyncio.sleep(3600)  # Check once every hour

client.run(my_secret)
