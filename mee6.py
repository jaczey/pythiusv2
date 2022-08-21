from mee6_py_api import API as mee6
import asyncio
import pymongo
from pymongo.server_api import ServerApi

async def claim(database, userID, guildID):
    api = mee6(guildID)
    level = await api.levels.get_user_level(userID)

    db = client['pythius']
    col = db['users']
    query = {"userID": str(userID)}

    data = col.find_one(query)

    if data is None:
        return ["Error", "Not created"]

    lastlevel = data['lastChanged']
    balance = data['balance']
    checkLevel = lastlevel
    status = None
    while status is None:
        checkLevel = checkLevel + 5
        if level < checkLevel:
            status = "Completed"

    checkLevel = checkLevel - 5
    reward = checkLevel - lastlevel
    reward = reward * 20
    if reward == 0:
        return ["Error", str(checkLevel)]
    newBalance = reward + balance

    query = {"userID": str(userID)}
    newvalues = {"$set": {"balance": newBalance, "lastChanged": checkLevel}}

    col.update_one(query, newvalues)
    return ["Success", [reward], [newBalance]]
    #reward, lastchanged(checklevel)

    #10$ = 100 PyCoins = 5 Level
    #1 Level = 2$

    # 5 = 100, 10 = 200, 15 = 300, 20 = 400, 25 = 500, 30 = 600

