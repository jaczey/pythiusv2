import asyncio

import discord
from discord.ext import commands
from discord import Option, SlashCommandOptionType, default_permissions
import balance as pythius
import marketplace as pyshop
import mee6
from datetime import datetime, timedelta
import pymongo
from pymongo.server_api import ServerApi

intents = discord.Intents.all()
client = commands.Bot(debug_guilds=[835693520865591327, 921049690265497621], intents=intents)
EditBalance = client.create_group(name="editbalance", description="Edit user's current balance")
Marketplace = client.create_group(name="shop", description="Marketplace commands")

database = pymongo.MongoClient(
        "mongodb+srv://danielsimon:nyJrfuUzL9AcQxKn@pythius.gb5zbzu.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))

@client.slash_command(description="Check balance")
async def balance(
        ctx
):
    await ctx.defer()
    userID = ctx.author.id
    status = pythius.getBalance(database, userID)
    if status is None:
        return await ctx.respond(
            f"Account for <@{ctx.author.id}> doesn't exist")
    else:
        return await ctx.respond(
            f"<@{ctx.author.id}>'s balance : {status}")

@client.slash_command(description="Claim PyCoins")
async def claim(
        ctx
):
    await ctx.defer()
    userID = ctx.author.id
    guildID = 921049690265497621
    status = await mee6.claim(database, userID, guildID)
    if status[0] == "Error":
        if status[1] == "Not created":
            return await ctx.respond(
                f"Account for <@{ctx.author.id}> doesn't exist")
        else:
            level = str(int(status[1]) + 5)
            return await ctx.respond(
                f"Reach Level {level} to claim your next reward")
    elif status[0] == "Success":
        return await ctx.respond(
            f"Successfully claimed {status[1][0]} PyCoins, <@{ctx.author.id}> new balance is {status[2][0]} PyCoins")


@client.slash_command(description="Create User Account")
async def createaccount(
        ctx,
):
    await ctx.defer()
    userID = ctx.author.id
    status = pythius.createAccount(database, userID)
    if status == str(ctx.author.id):
        return await ctx.respond(
            f"Account for <@{ctx.author.id}> already exists")
    elif status == "Success":
        return await ctx.respond(
            f"Successfully created account for <@{ctx.author.id}>")
    else:
        return await ctx.respond(
            f"Failed to create account for {ctx.author.name}, contact support.")


@Marketplace.command(description="Buy an item", pass_context=True)
async def buy(
        ctx,
        name: Option(SlashCommandOptionType.role, "Role you want to add", required=True)
):
    await ctx.defer()
    requirement = pyshop.checkRole(database, name.id)
    if not requirement:
        return await ctx.respond(
            f"Item isn't available in the shop")
    elif requirement == "None":
        rolecheck = discord.utils.get(ctx.author.roles, name=str(name.name))
        if rolecheck is not None and rolecheck.name == name.name:
            return await ctx.respond(
                f"User already has the item")
        else:
            status = pyshop.buyitem(database, ctx.author.id, name.id)
            if status == "User not found":
                return await ctx.respond(
                    f"User doesn't have an account yet, please create an account")
            elif status == "Item not found":
                return await ctx.respond(
                    f"Item doesn't exist in the shop")
            elif status == "item out of stock":
                return await ctx.respond(
                    f"Item is currently out of stock")
            elif status == "not enough balance":
                return await ctx.respond(
                    f"User doesn't have enough balance")
            elif status == "successful":
                role = name
                await ctx.author.add_roles(role)
                return await ctx.respond(
                    f"Successfully bought the role")
    elif requirement is not None:
        role = discord.utils.get(ctx.guild.roles, id=requirement)
        rolecheck = discord.utils.get(ctx.author.roles, name=str(role.name))
        if rolecheck is not None and rolecheck.name == role.name:
            rolecheck = discord.utils.get(ctx.author.roles, name=str(name.name))
            if rolecheck is not None and rolecheck.name == name.name:
                return await ctx.respond(
                    f"User already has the item")
            else:
                status = pyshop.buyitem(database, ctx.author.id, name.id)
                if status == "User not found":
                    return await ctx.respond(
                        f"User doesn't have an account yet, please create an account")
                elif status == "Item not found":
                    return await ctx.respond(
                        f"Item doesn't exist in the shop")
                elif status == "item out of stock":
                    return await ctx.respond(
                        f"Item is currently out of stock")
                elif status == "not enough balance":
                    return await ctx.respond(
                        f"User doesn't have enough balance")
                elif status == "successful":
                    role = name
                    await ctx.author.add_roles(role)
                    return await ctx.respond(
                        f"Successfully bought the role")
        else:
            return await ctx.respond(
                f"You don't have the role mentioned in requirements")


@Marketplace.command(description="Shows the available items")
async def show(
        ctx,
):
    await ctx.defer()
    items = pyshop.showshop(database)
    if len(items) == 0:
        return await ctx.respond(
            f"No items available at the moment")
    else:
        embed = discord.Embed(title="Pythius Shop", description="Buy items using PyCoins here")
        embed.set_thumbnail(url="https://img.icons8.com/nolan/344/online-shop.png")
        for x in range(len(items)):
            Item = items[x]
            Item = Item.split(",")
            if not Item[4] == "None":
                print(type(Item[4]))
                embed.add_field(name=f"{Item[0]}",
                                value=f"Role: <@&{Item[1]}> \n Price: {Item[3]} \n Left: {Item[2]} \n Requirement: <@&{Item[4]}>",
                                inline=False)
            else:
                embed.add_field(name=f"{Item[0]}",
                                value=f"Role: <@&{Item[1]}> \n Price: {Item[3]} \n Left: {Item[2]} \n Requirement: {Item[4]}",
                                inline=False)
        return await ctx.respond(embed=embed)


@Marketplace.command(description="Add an item")
@default_permissions(administrator=True)
async def add(
        ctx,
        role: Option(SlashCommandOptionType.role, "Role you want to add", required=True),
        amount: Option(SlashCommandOptionType.integer, "Amount of the role", required=True),
        price: Option(SlashCommandOptionType.integer, "Price of the role", required=True),
        requirement: Option(SlashCommandOptionType.role, "Requirement to buy this role", required=False)
):
    await ctx.defer()
    if role.name == "@everyone":
        return await ctx.respond("Invalid Role")
    if requirement is not None:
        result = pyshop.additem(database, role.name, role.id, amount, price, requirement.id)
    else:
        result = pyshop.additem(database, role.name, role.id, amount, price, requirement)
    if not result:
        return await ctx.respond(
            f"Role already exists in the shop or server error, contact support.")
    else:
        return await ctx.respond(
            f"Role successfully added to the shop.")


@Marketplace.command(description="Remove an item")
@default_permissions(administrator=True)
async def remove(
        ctx,
        role: Option(SlashCommandOptionType.role, "Role you want to add", required=True)
):
    await ctx.defer()
    if role.name == "@everyone":
        return await ctx.respond("Invalid Role")
    result = pyshop.removeitem(database, role.id)
    if result:
        return await ctx.respond(
            f"Role successfully removed from the shop.")
    else:
        return await ctx.respond(
            f"Role doesn't exist in the shop or server error, contact support.")


@EditBalance.command(description="Remove amount from user's balance")
@default_permissions(administrator=True)
async def remove(
        ctx,
        user: Option(SlashCommandOptionType.user, "User you want to remove balance of", required=True),
        amount: Option(SlashCommandOptionType.integer, "Amount you want to remove", required=True),
):
    await ctx.defer()

    userID = int(user.id)
    currentBalance = pythius.getBalance(database, userID)
    if currentBalance is None:
        return await ctx.respond(f"{user.mention} doesn't have an account yet")
    elif amount <= 0:
        return await ctx.respond(f"Amount must be greater than 0")
    elif currentBalance < amount:
        return await ctx.respond(
            f"{user.mention} has lower balanace than the amount inserted. `{user.name}'s  Balance = {currentBalance}`")

    newBalance = pythius.editBalance(database, userID, currentBalance, amount, 'remove')
    return await ctx.respond(
        f"Successfully removed {amount} from {user.mention}'s balance. `{user.name}'s Balance = {newBalance}`")


@EditBalance.command(description="Add amount to user's balance")
@default_permissions(administrator=True)
async def add(
        ctx,
        user: Option(SlashCommandOptionType.user, "User you want to add balance to", required=True),
        amount: Option(SlashCommandOptionType.integer, "Amount you want to add", required=True)
):
    await ctx.defer()

    userID = int(user.id)
    currentBalance = pythius.getBalance(database, userID)
    if currentBalance is None:
        return await ctx.respond(f"{user.mention} doesn't have an account yet")
    elif amount <= 0:
        return await ctx.respond(f"Amount must be greater than 0")

    newBalance = pythius.editBalance(database, userID, currentBalance, amount, 'add')
    return await ctx.respond(
        f"Successfully added {amount} to {user.mention}'s balance. `{user.name}'s Balance = {newBalance}`")

async def purger():
    now = datetime.utcnow()
    while True:
            if now.weekday() < 5:
                d = now - timedelta(weeks=1)
                d2 = now - timedelta(hours=1)
                users = []
                generalChannel = client.get_channel(929054598877024296)
                print(generalChannel)
                async for message in generalChannel.history(limit=None, before=d2, after=d):
                    users.append(message.author.id)

                degens = []
                babydegens = []
                guild = client.get_guild(921049690265497621)
                degenrole = discord.utils.get(guild.roles, id=961019236858343496)
                babydegen = discord.utils.get(guild, id=980051918485323807)

                for member in guild.members:
                    if degenrole in member.roles:
                        if member.id not in degens:
                            degens.append(member.id)

                        if babydegen in member.roles:
                            if member.id not in degens and member.id not in babydegens:
                                babydegens.append(member.id)

                for member in degens:
                    counter = 0
                    for i in users:
                        if counter < 100:
                            if member == i:
                                counter += 1
                        else:
                            break

                    if counter < 100:
                        member = guild.get_member(member)
                        print(f"{member.name} degen")
                        await member.remove_roles(degenrole)

                for member in babydegens:
                    counter = 0
                    for i in users:
                        if counter < 100:
                            if member == i:
                                counter += 1
                        else:
                            break

                    if counter < 100:
                        member = guild.fetch_member(member)
                        print(f"{member.name} baby degen")
                        await member.remove_roles(babydegen)

@client.event
async def on_ready():
    print('Logged in as ' + str(client.user))
    await purger()

client.run('MTAwODA3MzA5NTUxNDQyNzQ4Mg.Gfm_93.BGJRfzf8QCfwn6bML3SvHq8nbw8-5I9as2MeMU')
# Token = MTAwODA3MzA5NTUxNDQyNzQ4Mg.Gfm_93.BGJRfzf8QCfwn6bML3SvHq8nbw8-5I9as2MeMU
