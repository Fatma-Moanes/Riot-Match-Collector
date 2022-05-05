import requests
import time
import random
import json
#from google.colab import files


def get_leagues(platform, api):
    """
    Returns a list of 200 summonerNames from master, grandmaster and challenger leagues in the given platform.

    Inputs:
    - platform: One of these values ['BR1', 'eun1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'RU', 'TR1']
    - api: Your api key.

    Output:
    - summonerName: List of summoner Names in the given platform.
    """

    leagues = ['challengerleagues', 'grandmasterleagues', 'masterleagues']

    url_challenger = 'https://' + platform + '.api.riotgames.com/lol/league/v4/' + leagues[
        0] + '/by-queue/RANKED_SOLO_5x5?api_key=' + api
    response = requests.get(url_challenger)
    lis = response.json()['entries']
    summonerName_c = [sub['summonerName'] for sub in lis[0:67]]

    url_grandmaster = 'https://' + platform + '.api.riotgames.com/lol/league/v4/' + leagues[
        1] + '/by-queue/RANKED_SOLO_5x5?api_key=' + api
    response = requests.get(url_grandmaster)
    lis = response.json()['entries']
    summonerName_g = [sub['summonerName'] for sub in lis[0:67]]

    url_master = 'https://' + platform + '.api.riotgames.com/lol/league/v4/' + leagues[
        2] + '/by-queue/RANKED_SOLO_5x5?api_key=' + api
    response = requests.get(url_master)
    lis = response.json()['entries']
    summonerName_m = [sub['summonerName'] for sub in lis[0:66]]

    summonerName = summonerName_c + summonerName_g + summonerName_m

    return summonerName


def get_puuid(platform, api, summonerNames):
    """
    Returns a list of the puuids of each summoner of the given list of summoner names in a given platform.

    Inputs:
    - platform: One of these values ['BR1', 'eun1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'RU', 'TR1']
    - api: Your api key.
    - summonerNames: A list of summoner names in a given platform.

    Output:
    - puuid_list: A list of puuids of the summoners.
    """

    puuid_list = []
    for name in summonerNames:

        url = 'https://' + platform.lower() + '.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + name + '?api_key=' + api
        response = requests.get(url).json()

        # If any error happens, skip that summoner
        if response.get('status'):
            continue
        puuid = response['puuid']
        puuid_list.append(puuid)
        print(len(puuid_list))
    return puuid_list


def get_matchId(region, api, puuids):
    """
    Returns a list of match ids using the given list of puuids of summoners in a specific region.

    Inputs:
    - region: 'americas', 'asia' or 'europe'.
    - api: Your api key.
    - puuids: A list of puuids of summoners.

    Output:
    - matchId_list: A list of matches played by these summoners. 10 matches are retrieved for each summoner.

    """

    matchId_list = []
    for puuid in puuids:
        # Get the ids of 10 matches played by that summoner with the puuid
        url = 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/by-puuid/' + puuid + '/ids?start=0&count=10&api_key=' + api
        response = requests.get(url).json()

        # If rate limit is exceeded
        if isinstance(response, dict):
            print(response['status']['message'])
            # sleep for 2 minutes
            time.sleep(120)
            # then request again
            url = 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/by-puuid/' + puuid + '/ids?start=0&count=10&api_key=' + api
            response = requests.get(url).json()

        matchId_list.extend(response)

    return matchId_list


def get_matches(region, api, matchIds):
    """
    Get 1,000 random matches from the given matchIds list.

    Inputs:
    - region: 'americas', 'asia' or 'europe'.
    - api: Your api key.
    - matchIds: A list of matches played by summoners.

    Output:
    - matches: A dictionary containing 1000 matches.
    """
    matches = []
    i = 0
    random_indices = random.sample(range(0, len(matchIds) - 1), 1000)
    for ind in random_indices:
        time.sleep(0.01)
        url = 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/' + matchIds[ind] + '?api_key=' + api
        response = requests.get(url).json()

        # If rate limit is exceeded
        while response.get('status'):
            print(response['status']['message'])
            time.sleep(40)
            url = 'https://' + region + '.api.riotgames.com/lol/match/v5/matches/' + matchIds[ind] + '?api_key=' + api
            response = requests.get(url).json()

        i += 1
        print("Step = {}".format(i))
        matches.append(response)

    return matches


# This function wraps all of the above functions
def getMatchesFromPlatform(region, platform, api):
    """
    Get 1,000 random matches from the given platform, saves it in a file and dowlnoads it.

    Inputs:
    - region: 'americas', 'asia' or 'europe'.
    - platform: One of these values ['BR1', 'eun1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'RU', 'TR1']
    - api: Your api key.

     Output:
    - matches: A dictionary containing 1000 matches.

    """
    summonerNames = get_leagues(platform, api)
    puuids = get_puuid(platform, api, summonerNames)
    match_ids = get_matchId(region, api, puuids)
    matches = get_matches(region, api, match_ids)

    with open('matches', 'w') as f:
        json.dump(matches, f)

    #files.download("matches")

if __name__ == '__main__':
    api = 'YOUR API KEY'
    platform = ['BR1', 'eun1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1', 'OC1', 'RU', 'TR1']
    region = ['americas', 'asia', 'europe']

    matches = getMatchesFromPlatform(region[0], platform[0], api)
