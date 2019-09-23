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
import templates

loop = asyncio.get_event_loop()

def dataFile():

    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))

    dataLocation = str(path)

    return(dataLocation)

while True:
    try:

        client = discord.Client()
        
        if Path(dataFile() + "/Data/data.db").is_file():

            criticalData = {}
            configurations = []
            
            connection = sqlite3.connect(dataFile() + "/Data/data.db")
            toRun = connection.cursor()
            
            for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical"):
                criticalData[criticalKey] = criticalValue
                
            for row in toRun.execute("SELECT * FROM configurations"):
                configurations.append(row)
            
        else:
            raise Warning("Initial Setup Not Completed!")

        @client.event
        async def on_ready():
            print("---------------------------------------------------------------------------------------------------------------")
            print("[" + time.strftime("%A, %d %B at %H:%M:%S %Z") + "] Discord Relay Version 1.00 - Successfully Activated")
            print("---------------------------------------------------------------------------------------------------------------\n\n")
            print('Logged in as ' + client.user.name)

        @client.event
        async def on_message(message):
            global configurations
        
            stringTime = str(message.created_at.strftime("%d %B - %H:%M:%S UTC"))
            shortTime =	 str(message.created_at.strftime("%H:%M"))

            author = str(message.author.name)
            authorName = str(message.author.display_name)

            server = str(message.guild)

            channel = str(message.channel)

            content = str(message.content)
            
            for criticalKey, criticalValue in toRun.execute("SELECT * FROM critical WHERE key=?", ("lastupdate",)):
                lastUpdated = criticalValue
                
                if lastUpdated != criticalData["lastupdate"]:
                    
                    configurations = []
                    for row in toRun.execute("SELECT * FROM configurations"):
                        configurations.append(row)
                    
                    criticalData["lastupdate"] = lastUpdated
                    
            for configUUID, configName, configCreated, configDestination, configURL, configTemplate, configServer, configChannel, configAuthor, configKeyword in configurations:
                                    
                if configServer == "" or configServer.lower() == server.lower():
                    toPost = True
                else:
                    toPost = False
                    
                if toPost and (configChannel == "" or configChannel.lower() == channel.lower()):
                    toPost = True
                else:
                    toPost = False
                    
                if toPost and (configAuthor == "" or configAuthor.lower() == author.lower()):
                    toPost = True
                else:
                    toPost = False
                    
                if toPost and (configKeyword == "" or configKeyword.lower() in content.lower()):
                    toPost = True
                else:
                    toPost = False
                    
                if toPost:
                
                    template = templates.returnTemplate(configTemplate)
                    
                    toSend = template.format(longTime=stringTime, shortTime=shortTime, authorUsername=author, authorName=authorName, server=server, channel=channel, message=content)
                    reportingTime = int(time.time())                    

                    if configDestination == "Slackbot":
                        toSend=toSend.replace("@everyone", "@channel")
                        toSend=toSend.replace("**", "*")
                    
                    if configDestination == "Slack":
                        toSend=toSend.replace("@everyone", "<!channel>")
                        toSend=toSend.replace("**", "*")
                                            
                    uniqueMessageID = secrets.token_hex(8)
                    toRun.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?, ?)", (uniqueMessageID, reportingTime, server, channel, author, content, configUUID))
                    
                    connection.commit()
                    
                    if configDestination == "Slackbot":
                        result = sender.postToSlackbot(toSend, configURL)
                    
                    if configDestination == "Slack":
                        result = sender.postToSlack(toSend, configURL)
                    
                    if configDestination == "Discord":
                        result = sender.postToDiscord(toSend, configURL)
                    
                    if result:
                        print("[" + time.strftime("%d %B - %H:%M:%S UTC") + "] Message relayed to " + configName + ".")
        
        try:

            loop.run_until_complete(client.start(criticalData["token"]))
            
        except KeyboardInterrupt:
            print('Manual Shutdown Initiated')
            connection.close()
            
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
                
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)

        except:
            currentError = str(sys.exc_info()[1])
            for task in asyncio.Task.all_tasks(loop):
                task.cancel()
			
            connection.close()
            time.sleep(5)
            print(str(currentError) + " - Trying Again...")

    except KeyboardInterrupt:
        print('Manual Shutdown Initiated')
        connection.close()
        
        for task in asyncio.Task.all_tasks(loop):
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
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
		
        connection.close()
        time.sleep(5)
        print(str(currentError) + " - Trying Again...")