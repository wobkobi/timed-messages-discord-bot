import discord
import asyncio
from discord import app_commands, tasks
import sqlite3
from datetime import datetime, timedelta


intents = discord.Intents.default()
client = discord.Client(intents=intents)


def setup_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (reminder_id INTEGER PRIMARY KEY, user_id INTEGER, channel_id INTEGER, reminder TEXT, remind_time TIMESTAMP)''')
    conn.commit()
    conn.close()


@client.event
async def on_ready():
    print('Bot is ready.')
    remind_check.start()  # start the task when the bot is ready


@client.command(name='remindme')
async def remindme(ctx, time: str, *, reminder: str):
    unit = time[-1]
    if unit == 'h':
        remind_time = datetime.now() + timedelta(hours=int(time[:-1]))
    elif unit == 'd':
        remind_time = datetime.now() + timedelta(days=int(time[:-1]))
    elif unit == 'm':
        remind_time = datetime.now() + timedelta(days=int(time[:-1])*30)
    else:
        await ctx.send("Invalid time format.")
        return

    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("INSERT INTO reminders (user_id, channel_id, reminder, remind_time) VALUES (?, ?, ?, ?)",
              (ctx.author.id, ctx.channel.id, reminder, remind_time))
    conn.commit()
    conn.close()
    await ctx.send(f"Reminder set for {reminder} at {remind_time}")


@tasks.loop(seconds=60)  # check every minute
async def remind_check():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reminders WHERE remind_time <= ?",
              (datetime.now(),))
    reminders = c.fetchall()
    for row in reminders:
        channel = bot.get_channel(row[2])
        user = bot.get_user(row[1])
        await channel.send(f"{user.mention}, you asked to be reminded: {row[3]}")
        c.execute("DELETE FROM reminders WHERE reminder_id=?", (row[0],))
    conn.commit()
    conn.close()

setup_db()
client.run('your-bot-token')
