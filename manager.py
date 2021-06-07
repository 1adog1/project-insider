import discord
import asyncio
import json
import requests
import time
import sys
import os
import math
import inspect
import sqlite3
import secrets
import traceback

import sender

from pathlib import Path
from datetime import datetime, timedelta
from tabulate import tabulate

def dataFile():

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))

    dataLocation = str(path)

    return(dataLocation)

def syncConfigurations():
    global configurations
    
    configurations = []

    for row in toRun.execute("SELECT * FROM configurations"):
        configurations.append(row)

###############################
#----- Command Functions -----#
###############################

def initialSetup():
    global criticalData
    print("""
-------------------------------
PROJECT INSIDER - Initial Setup
-------------------------------

Welcome to initial setup! The relay just needs a few bits of information and we can get started!
Please make sure you have your app ready to go. 
    """)
    
    while True:
        newID = input("Please enter your client ID: ")
        newToken = input("Please enter your bot's token: ")
        
        criticalData["token"] = newToken
        criticalData["clientid"] = newID
        
        if testConnection():
            
            toRun.execute("DROP TABLE IF EXISTS critical")
            toRun.execute("CREATE TABLE critical (key text, value text)")
            toRun.execute("INSERT INTO critical VALUES (?, ?)", ("token", criticalData["token"]))
            toRun.execute("INSERT INTO critical VALUES (?, ?)", ("clientid", criticalData["clientid"]))
            toRun.execute("INSERT INTO critical VALUES (?, ?)", ("lastupdate", str(int(time.time()))))
            
            connection.commit()
            
            print("Setup Complete! Here's your share link to get started: ")
            
            generateJoinLink()
            
            print("Please be advised if the relay is currently running it will need to be restarted for these changes to take effect.\n")
            
            break
            
        else:
            print("Please re-enter your details.")

def showHelp():
    print("""
--------------------------
PROJECT INSIDER - Commands
--------------------------

Commands are NOT case sensitive. Arguments ARE case sensitive.

HELP - Prints this response.
STATUS - Prints a list of all configurations.
TEST - Tests your app settings to ensure a connection can be made. 
SHARE - Generates a link for you to give to server admins so your bot can join their server.
CREATE - Starts the creator for a new configuration. 
DELETE [uuid] - Deletes a configuration.
REPORT [uuid] - Prints a report detailing the history of a configuration.
LOGS - Prints a log of all relayed messages and their IDs.
RECALL [message_id] - Prints a previously relayed message.
SCRUB [author_name] - Deletes all log entries related to messages relayed from a specific user. (For compliance with the Discord Developers Terms of Service; Section 2.4)
WIPE - Completely wipes the logs.
RESET - Calls the Initial Setup tool so you can modify your app information while keeping your configurations intact.
    """)
    
def generateJoinLink():
    print("\nGive this link to a server owner for you to relay messages from their server: \nhttps://discord.com/api/oauth2/authorize?client_id=" + criticalData["clientid"] + "&scope=bot&permissions=66560\n")

def testConnection():
    loop = asyncio.get_event_loop()

    client = discord.Client()

    @client.event
    async def on_ready():

        print('\nTest Success! Token linked to: ' + client.user.name + ".\n")
        
        await client.close()
        
    try:
        loop.run_until_complete(client.start(criticalData["token"]))
                
        return True
    
    except:
        print("\nTest Failed!\n")
    
        return False

#############################
#----- Startup Process -----#
#############################
    
criticalData = {}
 
if Path(dataFile() + "/Data/data.db").is_file():
    
    connection = sqlite3.connect(dataFile() + "/Data/data.db")
    toRun = connection.cursor()
    
    for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical"):
        criticalData[criticalKey] = criticalValue
        
    syncConfigurations()
    
else:
    
    connection = sqlite3.connect(dataFile() + "/Data/data.db")
    toRun = connection.cursor()
    
    toRun.execute("CREATE TABLE critical (key text, value text)")
    toRun.execute("CREATE TABLE configurations (uuid text, name text, created integer, destination text, hookurl text, template text, server text, channel text, author text, keyword text, priority integer)")
    toRun.execute("CREATE TABLE reports (messageid text, created integer, server text, channel text, author text, message text, sentto text)")
    
    connection.commit()
    
    initialSetup()
    
    for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical"):
        criticalData[criticalKey] = criticalValue
        
    syncConfigurations()   
    
def startCreator():
    print("""
---------------------------------
PROJECT INSIDER - Creation Wizard
---------------------------------
    """)
    
    uniqueConfigurationID = secrets.token_hex(8)
    
    newName = input("Set a name for your configuration: ")
    print("""
What kind of relay are you creating?
0 - Discord Webhook
1 - Slack App Webhook
2 - Remote Slackbot Webhook
    """)
    
    typeOptions = [
    "Discord",
    "Slack",
    "Slackbot"
    ]
    
    while True:
        typeSelection = int(input("Enter the corresponding number: "))
        
        if typeSelection >= 0 and typeSelection < 3:
            newType = typeOptions[typeSelection]
            
            break
            
        else:
            print("No corresponding type, enter a number from the above possibilities.")
            
    newURL = input("Enter the URL of the webhook you'll be relaying to: ")

    templateOptions = [
    "Imitation",
    "Imitation w/ Username",
    "Monitoring",
    "Monitoring w/ Codeblocks",
    "Jabber",
    "Modern w/ Username",
    "Modern w/ Display"
    ]
    
    print("""
What kind of template would you like to use?
Example images can be found here: https://imgur.com/a/dwptAhn
0 - Imitation Post
1 - Imitation Post With Username
2 - Monitoring Post
3 - Monitoring Post With Codeblocks
4 - Jabber Imitation
5 - Modern Ping With Username
6 - Modern Ping With Display Name
    """)
    
    while True:
        templateSelection = int(input("Enter the corresponding number: "))
        
        if templateSelection >= 0 and templateSelection < 7:
            newTemplate = templateOptions[templateSelection]
            
            break
            
        else:
            print("No corresponding type, enter a number from the above possibilities.")
            
    print("\nThe following conditions can contain a single value, no value (no restriction), or more than one value in a comma-separated format.")
    
    newServer = input("Server names to restrict to: ")
    
    newServer = newServer.replace(", ", ",").lower()
    serverList = list(filter(None, newServer.split(",")))
    formattedServers = json.dumps(serverList)
    
    newChannel = input("Channel names to restrict to: ")
    
    newChannel = newChannel.replace(", ", ",").lower()
    channelList = list(filter(None, newChannel.split(",")))
    formattedChannels = json.dumps(channelList)
    
    newAuthor = input("Author usernames to restrict to: ")
    
    newAuthor = newAuthor.replace(", ", ",").lower()
    authorList = list(filter(None, newAuthor.split(",")))
    formattedAuthors = json.dumps(authorList)
    
    newKeyword = input("Keywords to restrict to: ")
    
    newKeyword = newKeyword.replace(" ", "").lower()
    keywordList = list(filter(None, newKeyword.split(",")))
    formattedKeywords = json.dumps(keywordList)
    
    print("""
What priority would you like this configuration to be?

Priorities are used to determine if a message should be relayed multiple times. They're integers that follow these rules:

 - Messages WILL ALWAYS be sent to configurations with priority -1, provided its conditions are met.
 - Messages will be sent to higher priority configurations first.
 - Messages WILL NOT be sent if a higher priority configuration has already relayed it.
 - Messages WILL be sent if an equal priority configuration has already relayed it. 
    """)
    
    while True:
    
        newPriority = int(input("Enter a priority: "))
        
        if newPriority >= -1:
        
            break
            
        else:
        
            print("Invalid Priority, you need to enter a priority of >= -1.")
    
    toNotify = input("\nIf you would like to send details of this configuration to the destination channel, type YES (case sensitive), otherwise type anything else: ")
    
    creationOccured = int(time.time())
    
    toRun.execute("INSERT INTO configurations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uniqueConfigurationID, newName, creationOccured, newType, newURL, newTemplate, formattedServers, formattedChannels, formattedAuthors, formattedKeywords, newPriority))    
    toRun.execute("UPDATE critical SET value=? WHERE key=?", (str(int(time.time())),"lastupdate"))
    
    connection.commit()
    
    syncConfigurations()
    
    if toNotify == "YES":
        toSend = "A New Relay Has Been Created!\n\nName: " + newName + "\nRestrictions:\n```\nServers: " + ",".join(serverList) + "\nChannels: " + ",".join(channelList) + "\nAuthors: " + ",".join(authorList) + "\nKeywords: " + ",".join(keywordList) + "\nPriority: " + str(newPriority) + "\n```"

        if newType == "Slackbot":
            sender.postToSlackbot(toSend, newURL)
        
        if newType == "Slack":
            sender.postToSlack(toSend, newURL)
        
        if newType == "Discord":
            sender.postToDiscord(toSend, newURL)
    
    print("\nConfiguration Created! If you opted to you should see a message in the destination channel detailing it. If you don't, delete it and try again.\n")

def deleteConfig(configID):
    actuallyExists = False

    for configUUID, configName in toRun.execute("SELECT uuid, name FROM configurations WHERE uuid=?", (configID,)):
        toRun.execute("DELETE FROM configurations WHERE uuid=?", (configID,))
        toRun.execute("UPDATE critical SET value=? WHERE key=?", (str(int(time.time())),"lastupdate"))
        
        connection.commit()
        
        syncConfigurations()
        
        print("\nThe configuration " + configName + " has been deleted.\n")
        
        actuallyExists = True
        
    if not actuallyExists:
       print("\nNo configuration with that UUID exists.\n")

def showStatus():
        
    listToDisplay = []
    
    for configUUID, configName, configCreated, configDestination, configURL, configTemplate, configServer, configChannel, configAuthor, configKeyword, configPriority in configurations:
        niceTime = datetime.utcfromtimestamp(configCreated).strftime('%d %B, %Y - %H:%M:%S')
        
        conditionsToPrint = "Servers: " + ",".join(json.loads(configServer)) + "\nChannels: " + ",".join(json.loads(configChannel)) + "\nAuthors: " + ",".join(json.loads(configAuthor)) + "\nKeywords: " + ",".join(json.loads(configKeyword))
    
        listToDisplay.append([configUUID, configName, niceTime, configDestination, configTemplate, conditionsToPrint, configPriority])
        
    print("\n" + tabulate(listToDisplay, headers=['UUID', 'Name', 'Created', 'Type', 'Template', 'Conditions', 'Priority'], tablefmt='grid') + "\n")
       
def generateReport(configID):
    listToDisplay = []
    times = []
    totalRelayed = 0
    latestRelay = 0
    firstRelay = math.inf
    
    idExists = False

    for configUUID, configName, configCreated, configDestination, configURL, configTemplate, configServer, configChannel, configAuthor, configKeyword, configPriority in toRun.execute("SELECT * FROM configurations WHERE uuid=?", (configID,)):
    
        niceTime = datetime.utcfromtimestamp(configCreated).strftime('%d %B, %Y - %H:%M:%S')
        
        conditionsToPrint = "Servers: " + ",".join(json.loads(configServer)) + "\nChannels: " + ",".join(json.loads(configChannel)) + "\nAuthors: " + ",".join(json.loads(configAuthor)) + "\nKeywords: " + ",".join(json.loads(configKeyword))
    
        listToDisplay.append([configUUID, configName, niceTime, configDestination, configTemplate, conditionsToPrint, configPriority])
        
        for logUUID, logTime, logServer, logChannel, logAuthor, logContent, logConfigID in toRun.execute("SELECT * FROM reports WHERE sentto=?", (configID,)):
            totalRelayed += 1
            
            times.append(logTime)
            
            if logTime > latestRelay:
                latestRelay = logTime
                
            if logTime < firstRelay:
                firstRelay = logTime
        
        if len(times) == 1:
            
            latestRelay = datetime.utcfromtimestamp(latestRelay).strftime('%d %B, %Y - %H:%M:%S')
            firstRelay = datetime.utcfromtimestamp(firstRelay).strftime('%d %B, %Y - %H:%M:%S')
            
            averageBetweenRelayed = "Only One Message Has Been Relayed"
        
        elif len(times) > 0:

            differences = [times[x + 1] - times[x] for x in range(len(times) - 1)]
            
            averageBetweenRelayed = sum(differences) / len(differences)
            
            averageBetweenRelayed = str(timedelta(seconds=averageBetweenRelayed))
            
            latestRelay = datetime.utcfromtimestamp(latestRelay).strftime('%d %B, %Y - %H:%M:%S')
            firstRelay = datetime.utcfromtimestamp(firstRelay).strftime('%d %B, %Y - %H:%M:%S')
            
        else:
            latestRelay = "Never"
            firstRelay = "Never"
            averageBetweenRelayed = "No Messages Have Been Relayed"
                    
        print("\n" + tabulate(listToDisplay, headers=['UUID', 'Name', 'Created', 'Type', 'Template', 'Conditions', 'Priority'], tablefmt='grid') + "\n\nCONFIGURATION ANALYSIS\n----------------------\nTotal Relayed: " + str(totalRelayed) + "\nFirst Relay: " + firstRelay + "\nMost Recent Relay: " + latestRelay + "\nAverage Time Between Relays: " + str(averageBetweenRelayed) + "\n")
        
        idExists = True
        
    if not idExists:
        print("\nNo configuration with that UUID exists.\n")

def showLogs():
    formattedLogs = []

    for logUUID, logTime, logServer, logChannel, logAuthor, logContent, logConfigID in toRun.execute("SELECT * FROM reports"):
        niceTime = datetime.utcfromtimestamp(logTime).strftime('%d %B, %Y - %H:%M:%S')
    
        formattedLogs.append([logUUID, niceTime, logServer, logChannel, logAuthor, logConfigID])
        
    print("\n" + tabulate(formattedLogs, headers=['UUID', 'Relayed', 'Server', 'Channel', 'Author', 'Configuration ID'], tablefmt='grid') + "\n")

def recallMessage(messageID):
    formattedRecall = []
    idExists = False

    for logUUID, logTime, logServer, logChannel, logAuthor, logContent, logConfigID in toRun.execute("SELECT * FROM reports WHERE messageid=?", (messageID,)):
        niceTime = datetime.utcfromtimestamp(logTime).strftime('%d %B, %Y - %H:%M:%S')
    
        formattedRecall.append([logUUID, niceTime, logServer, logChannel, logAuthor, logConfigID])
        
        print("\n" + tabulate(formattedRecall, headers=['UUID', 'Relayed', 'Server', 'Channel', 'Author', 'Configuration ID'], tablefmt='grid') + "\n\nFULL MESSAGE\n------------\n" + logContent + "\n")
        
        idExists = True
        
    if not idExists:
        print("\nNo message with that UUID exists.\n")

def scrubAuthor(authorUsername):

    confirmation = input("Are you sure you want to scrub logs pertaining to this username? Type YES to confirm: ")

    if confirmation == "YES":
        toRun.execute("DELETE FROM reports WHERE author=?", (authorUsername,))
        
        connection.commit()
        
        print("\nLogs Scrubbed.\n")
        
    else:
        print("\nCancelling.\n")

def wipeLogs():

    confirmation = input("Are you sure you want to wipe all logs? Type YES to confirm: ")

    if confirmation == "YES":
        toRun.execute("DELETE FROM reports")
        
        connection.commit()
        
        print("\nAll Logs Deleted.\n")
        
    else:
        print("\nCancelling.\n")

################################
#----- Command Dictionary -----#
################################

commandKey = {
"HELP":{"Function":showHelp, "Has Argument":False},
"STATUS":{"Function":showStatus, "Has Argument":False},
"TEST":{"Function":testConnection, "Has Argument":False},
"SHARE":{"Function":generateJoinLink, "Has Argument":False},
"CREATE":{"Function":startCreator, "Has Argument":False},
"DELETE":{"Function":deleteConfig, "Has Argument":True},
"REPORT":{"Function":generateReport, "Has Argument":True},
"LOGS":{"Function":showLogs, "Has Argument":False},
"RECALL":{"Function":recallMessage, "Has Argument":True},
"SCRUB":{"Function":scrubAuthor, "Has Argument":True},
"WIPE":{"Function":wipeLogs, "Has Argument":False},
"RESET":{"Function":initialSetup, "Has Argument":False},
}

##########################
#----- Command Loop -----#
##########################

print("""
-------------------------
PROJECT INSIDER - Manager
-------------------------

""")
    
while True:
    newCommand = input("Please Enter a Command: ")
    
    parsedCommand = newCommand.split(" ")
    baseCommand = parsedCommand[0].upper()
    if len(parsedCommand) > 1:
        commandArgument = parsedCommand[1]
    
    if baseCommand in commandKey:
        commandInfo = commandKey[baseCommand]
        
        if commandInfo["Has Argument"]:
            if len(parsedCommand) > 1:
                commandInfo["Function"](commandArgument)
            else:
                print("\nThat Command Requires an Argument.\n")
        else:
            commandInfo["Function"]()
        
    else:
        print("\nUnrecognized Command! Type HELP for more info.\n")
