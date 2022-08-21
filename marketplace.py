import pymongo
from pymongo.server_api import ServerApi

#roleid,left,price,requirement
def showshop(database):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    shop = db['shop']

    items = []
    for x in shop.find():
        if x['amount'] > 0:
            item = x['roleName'] + ',' + x['roleID'] + ',' + str(x['amount']) + ',' + str(x['price']) + ',' + x['requirement']
            items.append(item)
        else:
            query = {"roleID": x['roleID']}
            data = shop.delete_one(query)

    return items

def additem(database, roleName, roleID, amount, price, requirement):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    shop = db['shop']

    query = {"roleID": str(roleID)}
    data = shop.find_one(query)

    if data is None:
        mydict = {"roleName": str(roleName), "roleID": str(roleID), "amount":int(amount), "price":int(price), "requirement":str(requirement)}

        x = shop.insert_one(mydict)

        if x:
            return True
        else:
            return False
    else:
        return False

def removeitem(database, roleID):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    shop = db['shop']

    query = {"roleID": str(roleID)}
    data = shop.find_one(query)

    if data is not None:
        query = {"roleID": str(roleID)}
        data = shop.delete_one(query)
        if data.deleted_count > 0:
            return True
        else:
            return False
    else:
        return False

def checkRole(database, roleID):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    shop = db['shop']

    query = {"roleID": str(roleID)}
    data = shop.find_one(query)

    if data is not None:
        requirement = data['requirement']
        return requirement
    else:
        return False

def buyitem(database, userID, roleID):
    client = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

    db = client['pythius']
    shop = db['shop']
    col = db['users']

    query = {"userID": str(userID)}
    data = col.find(query)
    result = None
    for x in data:
        result = x['balance']
        currentBalance = result
        query = {'roleID' : str(roleID)}
        data = shop.find(query)
        result2 = None

        for y in data:
            price = y['price']
            amount = y['amount']
            result2 = "Found"
            if amount > 0:
                if price <= currentBalance:
                    newBalance = currentBalance - price

                    query = {"userID": str(userID)}
                    newvalues = {"$set": {"balance": newBalance}}

                    col.update_one(query, newvalues)

                    newAmount = amount - 1
                    query = {"roleID": str(roleID)}
                    newvalues = {"$set": {"amount": newAmount}}

                    shop.update_one(query, newvalues)
                    result2 = "successful"
                    return result2
                else:
                    result2 = "not enough balance"
                    return result2
            else:
                result2 = "item out of stock"
                return result2
        if result2 is None:
            return "Item not found"
    if result is None:
        return "User not found"



