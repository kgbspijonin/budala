from multiprocessing.context import Process

import discord
import requests
from json import loads
import asyncio
from threading import Thread, Semaphore
from time import sleep, time
import discord.ext.tasks
import logging

class Lobby:
    def __init__(self, lobby, message):
        self.lobby = lobby
        self.message = message

    lobby = None
    message = None

class DClient(discord.Client):
    profiles = None
    profilesAdded = []

    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix="budala")

    async def on_ready(self):

        logger = logging.getLogger("budala")
        logger.setLevel(logging.ERROR)

        fh = logging.FileHandler("log.txt")
        fh.setLevel(logging.ERROR)

        logger.addHandler(fh)

        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        messages = await self.get_channel(807359181354041376).history(limit=200).flatten()
        self.profiles = await self.get_channel(810631887009480704).history(limit=200).flatten()
        newProfiles = []
        for profile in self.profiles:
            p = profile.content
            if (p[-1] == '/'):
                p = p[:-1]
            p = p[p.rindex('/') + 1:]
            newProfiles.append(p)
        self.profiles = newProfiles
        for message in messages:
            if(message.author.name == self.user.name and message.author.discriminator == self.user.discriminator):
                await message.delete()
        self.fetchLobbies.start()

    def flatten(self, lobby, path, value):
        item = lobby
        for i in path:
            item = item[i]
        vals = []
        for i in item:
            vals.append(i[value])
        return vals

    def getMatchEmbed(self, lobby):
        description = f"SPECTATE: <aoe2de://1/{lobby['match_id']}>\n"
        for team in set(self.flatten(lobby, ('players', ), 'team')):
            description += f"Team {team}:\n"
            for player in lobby['players']:
                if(player['team'] == team):
                    description += f"{f'''{player['name']} [{'(BG) ' if player['country']=='BG' else ''}r{player['rating']}''' if player['name'] is not None else f'AI['} as {civs[player['civ']-1]}]\n"
        embed = discord.Embed(title=f"Started game of {lobby['players'][0]['name']}: {lobby['name']}",
                              description=description)
        return embed

    def getLobbyEmbed(self, lobby):
        embed = discord.Embed(title=f"BG Lobby of {lobby['players'][0]['name']} [r{lobby['players'][0]['rating']}]: {lobby['name']}",
                              description=f"JOIN: <aoe2de://0/{lobby['match_id']}>")
        return embed

    def getRecordEmbed(self, lobby):
        description = f"DOWNLOAD: <https://aoe.ms/replay/?gameId={lobby['match_id']}&profileId={lobby['players'][0]['profile_id']}>\n"
        for team in set(self.flatten(lobby, ('players',), 'team')):
            description += f"Team {team}:\n"
            for player in lobby['players']:
                if (player['team'] == team):
                    description += f"{f'''{player['name']} [{'(BG) ' if player['country'] == 'BG' else ''}r{player['rating']}''' if player['name'] is not None else f'AI['} as {civs[player['civ'] - 1]}]\n"
        embed = discord.Embed(title=f"{'RANKED ' if lobby['name'] == 'AUTOMATCH' else 'UNRANKED '}Recorded game of {lobby['players'][0]['name']}: {lobby['name']}",
                              description=description)
        return embed

    async def handleLobbies(self):
        isLobbyBG = False
        lobbies = requests.get('https://aoe2.net/api/lobbies?game=aoe2de').text
        json = loads(lobbies)
        currentLobbyIds = []
        activeLobbyIds = []
        for activelobby in activeLobbies:
            activeLobbyIds.append(activelobby.lobby['match_id'])
        for lobby in json:
            isLobbyBG = False
            if (lobby['match_id'] not in activeLobbyIds):
                player = lobby['players'][0]
                if (player['country'] == 'BG' or player['name'] in neBulgari):
                    print("lobby:" + lobby['name'])
                    if (player['steam_id'] not in self.profiles and player['steam_id'] not in self.profilesAdded):
                        self.profilesAdded.append(player['steam_id'])
                        try:
                            inted = int(player['steam_id'])
                            profilemsg = await self.get_channel(PROFILES_CHANNEL_ID).send(
                                'https://steamcommunity.com/profiles/' + str(inted))
                        except:
                            profilemsg = await self.get_channel(PROFILES_CHANNEL_ID).send(
                                'https://steamcommunity.com/id/' + player['steam_id'])
                    if (isLobbyBG == False):  # LOBBY IS BG, BUT NO EMBED YET
                        embed = self.getLobbyEmbed(lobby)
                        message = await self.get_channel(CHANNEL_ID).send(embed=embed)
                        activeLobbies.append(Lobby(lobby, message))
                    isLobbyBG = True
            currentLobbyIds.append(lobby['match_id'])
        for lobby in activeLobbies:
            if (lobby.lobby['match_id'] not in currentLobbyIds):
                await lobby.message.delete()
                activeLobbies.remove(lobby)

    async def handleMatches(self):
        isLobbyBG = False
        matches = requests.get(f'https://aoe2.net/api/matches?game=aoe2de&since={int(time()) - 60*15}').text
        json = loads(matches)
        currentMatchIds = []
        activeLobbyIds = []
        for activelobby in activeMatches:
            activeLobbyIds.append(activelobby.lobby['match_id'])
        for lobby in json:
            isLobbyBG = False
            if (lobby['match_id'] not in activeLobbyIds):
                for player in lobby['players']:
                    if (player['country'] == 'BG' or player['name'] in neBulgari):
                        print("match:" + lobby['name'])
                        if (player['steam_id'] not in self.profiles and player['steam_id'] not in self.profilesAdded):
                            self.profilesAdded.append(player['steam_id'])
                            try:
                                inted = int(player['steam_id'])
                                profilemsg = await self.get_channel(PROFILES_CHANNEL_ID).send(
                                    'https://steamcommunity.com/profiles/' + str(inted))
                            except:
                                profilemsg = await self.get_channel(PROFILES_CHANNEL_ID).send(
                                    'https://steamcommunity.com/id/' + player['steam_id'])
                        if(isLobbyBG == False):   # LOBBY IS BG, BUT NO EMBED YET
                            embed = self.getMatchEmbed(lobby)
                            message = await self.get_channel(CHANNEL_ID).send(embed=embed)
                            activeMatches.append(Lobby(lobby, message))
                        isLobbyBG = True
            currentMatchIds.append(lobby['match_id'])
        for lobby in activeMatches:
            if (lobby.lobby['match_id'] not in currentMatchIds):
                    await lobby.message.delete()
                    activeMatches.remove(lobby)
                    embed = self.getRecordEmbed(lobby.lobby)
                    gamemsg = await self.get_channel(RECS_CHANNEL_ID).send(embed=embed)

    @discord.ext.tasks.loop()
    async def fetchLobbies(self):
        await self.wait_until_ready()
        while not self.is_closed():
            print("lobby fetch started")
            await self.handleLobbies()
            await self.handleMatches()
        print("dead")

    def tryexec(self, code):
        try:
            exec(code)
        except:
            pass

if __name__ == '__main__':
    lobbyFetcher = None

    neBulgari = ["IYI_TheNoobster", "ElizaKolmakov"]
    civs = ['Aztecs', 'Britons', 'Bulgarians', 'Burgundians', 'Burmese', 'Byzantines', 'Celts', 'Chinese', 'Cumans',
            'Ethiopians', 'Franks', 'Goths', 'Huns', 'Incas', 'Indians', 'Italians', 'Japanese', 'Khmer', 'Koreans',
            'Lithuanians', 'Magyars', 'Malay', 'Malians', 'Mayans', 'Mongols', 'Persians', 'Portuguese', 'Saracens',
            'Sicilians', 'Slavs', 'Spanish', 'Tatars', 'Teutons', 'Turks', 'Vietnamese', 'Vikings']

    CHANNEL_ID = 807359181354041376
    RECS_CHANNEL_ID = 850029907445809173
    PROFILES_CHANNEL_ID = 810631887009480704

    activeMatches = []
    activeLobbies = []
    client = DClient()

    client.run('')
