import pymongo
from pymongo.server_api import ServerApi
from datetime import datetime

def createAccount(database, userID):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    col = db['users']

    userID = str(userID)

    query = {"userID": str(userID)}
    data = col.find(query)
    result = "Not created"
    for x in data:
        result = x['userID']

    if result == "Not created":
        mydict = {"userID": userID, "balance": 0, "lastChanged": 0}
        x = col.insert_one(mydict)
        if x:
            return "Success"
        else:
            return "Failed"
    else:
        return result
def getBalance(database, userID):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    col = db['users']

    query = {"userID": str(userID)}
    data = col.find(query)

    result = None
    for x in data:
        result = x['balance']

    return result

def editBalance(database, userID, balance, amount, changes):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    col = db['users']

    currentBalance = balance
    newBalance = 0
    if changes == 'add':
        newBalance = currentBalance + amount
    elif changes == 'remove':
        newBalance = currentBalance - amount

    query = {"userID": str(userID)}
    newvalues = {"$set": {"balance": newBalance}}

    col.update_one(query, newvalues)

    return newBalance


