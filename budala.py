import discord
import threading
import time
import requests
import json
import asyncio
from json import loads
from threading import Thread

lobbyFetcher = None

neBulgari = ["IYI_TheNoobster", "ElizaKolmakov"]

activeLobbies = []

class ActiveLobby:
    def __init__(self, lobby, message):
        self.lobby = lobby
        self.message = message

    lobby = None
    message = None

class DClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.fetchLobbies())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def fetchLobbies(self):
        await self.wait_until_ready()
        while not self.is_closed():
            lobbies = requests.get('https://aoe2.net/api/lobbies?game=aoe2de').text
            json = loads(lobbies)
            lobbyIds = []
            activeLobbyIds = []
            for activelobby in activeLobbies:
                activeLobbyIds.append(activelobby.lobby)
            for lobby in json:
                if(lobby['match_id'] not in activeLobbyIds):
                    if(lobby['players'][0]['country'] == 'BG' or lobby['players'][0]['name'] in neBulgari):
                        print("bg lobby:" + lobby['name'])

                        embed = discord.Embed(title=f"BG Lobby of {lobby['players'][0]['name']}: {lobby['name']}",
                        description = f"<aoe2de://0/{lobby['match_id']}>")
                        message = await self.get_channel(807359181354041376).send(embed=embed)
                        activeLobbies.append(ActiveLobby(lobby['match_id'], message))
                lobbyIds.append(lobby['match_id'])
            for lobby in activeLobbies:
                if(lobby.lobby not in lobbyIds):
                    activeLobbies.remove(lobby)
                    await lobby.message.delete()

client = DClient()

client.run('ODA2OTM4MDYzODU4Njk2MjUz.YBwtog.DWj6stYb9mGSjLV1D32358AjNTk')
