from multiprocessing.context import Process

import discord
import requests
from json import loads
import asyncio
from threading import Thread, Semaphore
from time import sleep

class Proxy:
    def __init__(self, action, lobby):
        self.action = action
        self.lobby = lobby

    lobby = None
    action = None
    embed = None
    message = None

class ActiveLobby:
    def __init__(self, lobby, message):
        self.lobby = lobby
        self.message = message

    lobby = None
    message = None

class DClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix="budala")
        self.bg_task = self.loop.create_task(self.fetchLobbies())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def getStartedEmbed(self, lobby):
        description = f"Match Info:\n"
        description.join(f"Map: {lobby['map']}")
        for p in lobby['players']:
            if(p['slot_type'] == 1):
                description.join(f"")
        embed = discord.Embed(title=f"Started game of {lobby['players'][0]['name']}: {lobby['name']}",
                              description=f"<https://aoe2.net/s/{lobby['match_id']}>")

    async def fetchLobbies(self):
        await self.wait_until_ready()
        messages = await self.get_channel(807359181354041376).history(limit=200).flatten()
        for message in messages:
            if(message.author.name == self.user.name and message.author.discriminator == self.user.discriminator):
                await message.delete()

        while not self.is_closed():
            for proxy in activeProxies:
                if(proxy.action=="delete"):
                    for awaitproxy in activeProxies:
                        if(awaitproxy.action=="await"):
                            if(proxy.lobby['match_id'] == awaitproxy.lobby['match_id']):
                                await awaitproxy.message.delete()
                                activeProxies.remove(proxy)
                                activeProxies.remove(awaitproxy)
                elif(proxy.action=="send"):
                    embed = self.getStartedEmbed(proxy.lobby)
                    proxy.embed = embed
                    proxy.action = "await"
                    proxy.message = await self.get_channel(807359181354041376).send(embed=embed)

            lobbies = requests.get('https://aoe2.net/api/lobbies?game=aoe2de').text
            json = loads(lobbies)
            lobbyIds = []
            activeLobbyIds = []
            for activelobby in activeLobbies:
                activeLobbyIds.append(activelobby.lobby['match_id'])
            for lobby in json:
                if(lobby['match_id'] not in activeLobbyIds):
                    if(lobby['players'][0]['country'] == 'BG' or lobby['players'][0]['name'] in neBulgari):
                        print("bg lobby:" + lobby['name'])

                        embed = discord.Embed(title=f"BG Lobby of {lobby['players'][0]['name']}: {lobby['name']}",
                        description = f"<aoe2de://0/{lobby['match_id']}>")
                        message = await self.get_channel(807359181354041376).send(embed=embed)
                        activeLobbies.append(ActiveLobby(lobby, message))
                lobbyIds.append(lobby['match_id'])
            for lobby in activeLobbies:
                if(lobby.lobby['match_id'] not in lobbyIds):
                    await lobby.message.delete()
                    activeLobbies.remove(lobby)
                    _thread = Thread(target=asyncio.run, args=(self.handleStartedLobby(lobby.lobby, 15),))
                    _thread.start()

    async def handleStartedLobby(self, lobby, mins):
        activeProxies.append(Proxy("send", lobby))
        sleep(mins * 60)
        activeProxies.append(Proxy("delete", lobby))

if __name__ == '__main__':
    lobbyFetcher = None

    neBulgari = ["IYI_TheNoobster", "ElizaKolmakov"]

    activeProxies = []
    activeLobbies = []
    client = DClient()

    client.run('ODA2OTM4MDYzODU4Njk2MjUz.YBwtog.455-d_fyk3FDuqnnhxbUOt3T9pE')
