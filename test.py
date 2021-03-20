import discord
import requests
from json import loads

import time
import _thread
from threading import Thread
import asyncio

async def delayed(thread_name, delay):
    time.sleep(delay)
    return thread_name

async def print_time(threadName, delay):
    while 1:
        a = await delayed(threadName, delay)
        print(a + " " + time.ctime(time.time()))


# Create two threads as follows
try:
    _thread = Thread(target=asyncio.run, args=(print_time("1", 1),))
    _thread.start()
    _thread = Thread(target=asyncio.run, args=(print_time("2", 2),))
    _thread.start()

except:
    print("Error: unable to start thread")

while 1:
    time.sleep(10)
    print("main " + time.ctime(time.time()))