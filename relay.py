import discord
import asyncio
import json
import requests
import time
import sys
import os
import inspect
import sqlite3
import secrets

from pathlib import Path

import sender
import objects

configurations = []
loop = asyncio.get_event_loop()

intents = discord.Intents(messages=True, message_content=True, guilds=True)

def dataFile():

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))

    dataLocation = str(path)

    return(dataLocation)

while True:
    try:

        client = discord.Client(intents=intents)
        
        if Path(dataFile() + "/Data/data.db").is_file():

            criticalData = {}
            
            connection = sqlite3.connect(dataFile() + "/Data/data.db")
            toRun = connection.cursor()
            
            for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical"):
                criticalData[criticalKey] = criticalValue
            
            #Deleting any existing configurations
            amountOfConfigs = len(configurations)
            for x in range(0, amountOfConfigs):
                del configurations[0]
            
            for configUUID, configName, configCreated, configDestination, configURL, configTemplate, configServers, configChannels, configAuthors, configKeywords, configPriority, configTranslation in toRun.execute("SELECT * FROM configurations ORDER BY priority DESC, uuid ASC"):
            
                configurations.append(
                    objects.Configuration(
                        configUUID, 
                        configName, 
                        configDestination, 
                        configURL, 
                        configTemplate, 
                        json.loads(configServers), 
                        json.loads(configChannels), 
                        json.loads(configAuthors), 
                        json.loads(configKeywords), 
                        configPriority,
                        configTranslation
                    )
                )
            
        else:
            raise Warning("Initial Setup Not Completed!")

        @client.event
        async def on_ready():
            print("---------------------------------------------------------------------------------------------------------------")
            print("[" + time.strftime("%A, %d %B at %H:%M:%S %Z") + "] Discord Relay Version 3.00 - Successfully Activated")
            print("---------------------------------------------------------------------------------------------------------------\n\n")
            print("Logged in as " + client.user.name)

        @client.event
        async def on_message(message):
            global configurations, criticalData
        
            stringTime = str(message.created_at.strftime("%d %B - %H:%M:%S UTC"))
            shortTime =	 str(message.created_at.strftime("%H:%M"))

            author = str(message.author.name)
            authorName = str(message.author.display_name)

            server = str(message.guild)

            channel = str(message.channel)

            content = str(message.content)
            
            for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical"):
            
                if criticalKey == "lastupdate" and criticalValue != criticalData["lastupdate"]:
                
                    #Deleting any existing configurations
                    amountOfConfigs = len(configurations)
                    for x in range(0, amountOfConfigs):
                        del configurations[0]
                    
                    for configUUID, configName, configCreated, configDestination, configURL, configTemplate, configServers, configChannels, configAuthors, configKeywords, configPriority, configTranslation in toRun.execute("SELECT * FROM configurations ORDER BY priority DESC, uuid ASC"):
                    
                        configurations.append(
                            objects.Configuration(
                                configUUID, 
                                configName, 
                                configDestination, 
                                configURL, 
                                configTemplate, 
                                json.loads(configServers), 
                                json.loads(configChannels), 
                                json.loads(configAuthors), 
                                json.loads(configKeywords), 
                                configPriority,
                                configTranslation
                            )
                        )
                        
                criticalData[criticalKey] = criticalValue
                    
            currentPriority = 0
            for eachConfig in configurations:
                    
                if eachConfig.checkToPost(server, channel, author, content, currentPriority):
                
                    if "translationurl" in criticalData and "translationapikey" in criticalData:
                    
                        eachConfig.sendMessage(stringTime, shortTime, author, authorName, server, channel, content, criticalData["translationurl"], criticalData["translationapikey"])
                    
                    else:
                    
                        eachConfig.sendMessage(stringTime, shortTime, author, authorName, server, channel, content)
                    
                    currentPriority = eachConfig.priority
                
                    uniqueMessageID = secrets.token_hex(8)
                    toRun.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?)", (uniqueMessageID, int(time.time()), server, channel, author, content, eachConfig.UUID))
                    
                    connection.commit()
        
        try:

            loop.run_until_complete(client.start(criticalData["token"]))
            
        except KeyboardInterrupt:
            print("Manual Shutdown Initiated")
            connection.close()
            
            for task in asyncio.all_tasks(loop):
                task.cancel()
                
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

        except:
            currentError = str(sys.exc_info()[1])
            for task in asyncio.all_tasks(loop):
                task.cancel()
			
            connection.close()
            time.sleep(5)
            print(str(currentError) + " - Trying Again...")

    except KeyboardInterrupt:
        print("Manual Shutdown Initiated")
        connection.close()
        
        for task in asyncio.all_tasks(loop):
            task.cancel()
            
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
    except Warning:
        connection.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)        

    except:
        currentError = str(sys.exc_info()[1])
        for task in asyncio.all_tasks(loop):
            task.cancel()
		
        connection.close()
        time.sleep(5)
        print(str(currentError) + " - Trying Again...")
