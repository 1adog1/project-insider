import time
import re
import json
import requests
import secrets

import sender




###########################################
#----- Manager Configuration Creator -----#
###########################################

class Creator:

    def __init__(self, databaseConnection, criticalData):
    
        self.databaseConnection = databaseConnection
        self.databaseCursor = self.databaseConnection.cursor()
        self.criticalData = criticalData
        
        self.start()
        
    def start(self):
    
        print("""
        -----------------------------------------
            PROJECT INSIDER - Creation Wizard
        -----------------------------------------
        """)
        
        self.id = secrets.token_hex(8)
        self.setName()
        self.setDestination()
        self.setURL()
        self.setTemplate()
        self.setConditions()
        self.setPriority()
        self.setTranslation()
        self.insertConfiguration()
        
        toNotify = input("\nIf you would like to send details of this configuration to the destination channel, type YES (case sensitive), otherwise type anything else: ")
        
        if toNotify == "YES":
        
            self.notifyChannel()
            
        print("""
        Configuration Created!
        
        If you opted to you should see a message in the destination channel detailing it. If you don't, delete it and try again.
        """)
        
    def setName(self):
    
        self.name = input("Set a name for your configuration: ")
    
    def setDestination(self):
    
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
            typeSelection = int(input("Enter the number corresponding to your selection: "))
            
            if typeSelection >= 0 and typeSelection < 3:
                self.destination = typeOptions[typeSelection]
                
                break
                
            else:
                print("No corresponding type, enter a number from the above possibilities.")
    
    def setURL(self):
    
        self.url = input("Enter the URL of the webhook you'll be relaying to: ")
    
    def setTemplate(self):
    
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
            templateSelection = int(input("Enter the number corresponding to your selection: "))
            
            if templateSelection >= 0 and templateSelection < 7:
                self.template = templateOptions[templateSelection]
                
                break
                
            else:
                print("No corresponding type, enter a number from the above possibilities.")
    
    def setConditions(self):
    
        print("""
        The following parameters will set the conditions that have to be met for a message to be relayed.
        
        Each condition can contain a single value, no value (which means no restriction), or multiple values in a comma-seperated format (which is treated as an OR logical restriction). 
        """)
    
        newServer = input("Server names to restrict to: ")
        
        newServer = newServer.replace(", ", ",").lower()
        self.serverList = list(filter(None, newServer.split(",")))
        self.servers = json.dumps(self.serverList)
        
        newChannel = input("Channel names to restrict to: ")
        
        newChannel = newChannel.replace(", ", ",").lower()
        self.channelList = list(filter(None, newChannel.split(",")))
        self.channels = json.dumps(self.channelList)
        
        newAuthor = input("Author usernames to restrict to: ")
        
        newAuthor = newAuthor.replace(", ", ",").lower()
        self.authorList = list(filter(None, newAuthor.split(",")))
        self.authors = json.dumps(self.authorList)
        
        newKeyword = input("Keywords to restrict to: ")
        
        newKeyword = newKeyword.replace(" ", "").lower()
        self.keywordList = list(filter(None, newKeyword.split(",")))
        self.keywords = json.dumps(self.keywordList)
    
    def setPriority(self):
    
        print("""
        What priority would you like this configuration to be?

        Priorities are used to determine if a message should be relayed multiple times. They're integers that follow these rules:

         - Messages WILL ALWAYS be sent to configurations with priority -1, provided its conditions are met.
         - Messages will be sent to higher priority configurations first.
         - Messages WILL NOT be sent if a higher priority configuration has already relayed it.
         - Messages WILL be sent if an equal priority configuration has already relayed it. 
        """)
        
        while True:
        
            self.priority = int(input("Enter a priority: "))
            
            if self.priority >= -1:
            
                break
                
            else:
            
                print("Invalid Priority, you need to enter a priority of >= -1.")
    
    def setTranslation(self):
    
        if "translationurl" in self.criticalData and "translationapikey" in self.criticalData:
        
            while True:
            
                newTranslation = input("Enter a valid translation model (usually ??-??), or leave blank to not translate messages: ")
                
                if newTranslation == "":
                
                    self.translation = None
                    
                    break
                    
                elif self.testTranslation(newTranslation):
                    
                        self.translation = newTranslation
                        
                        break
                    
        else:
        
            self.translation = None
            
    def testTranslation(self, newTranslation):
    
        testingURL = self.criticalData["translationurl"] + "/v3/models/" + newTranslation + "?version=2018-05-01"
        authTuple = ("apikey", self.criticalData["translationapikey"])
        
        testCall = requests.get(testingURL, auth=authTuple)
        
        if testCall.status_code == requests.codes.ok:
        
            testResponse = json.loads(testCall.text)
        
            if "status" in testResponse and testResponse["status"] == "available":
            
                return True
                
            elif "status" in testResponse:
            
                print("The model you selected is not currently available. Its status is: " + testResponse["status"])
            
                return False
            
            else:
            
                print("The model you selected is not currently available.")
                
                return False
            
        else:
        
            print("Invalid Model, the format for base models is ??-??, where each ?? is a language id.")
            
            return False
    
    def insertConfiguration(self):
    
        creationOccured = int(time.time())
        
        self.databaseCursor.execute("INSERT INTO configurations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.id, self.name, creationOccured, self.destination, self.url, self.template, self.servers, self.channels, self.authors, self.keywords, self.priority, self.translation))
        
        self.databaseConnection.commit()
        self.databaseCursor.close()
    
    def notifyChannel(self):
    
        toSend = "A New Relay Has Been Created!\n\nName: " + self.name + "\nRestrictions:\n```\nServers: " + ",".join(self.serverList) + "\nChannels: " + ",".join(self.channelList) + "\nAuthors: " + ",".join(self.authorList) + "\nKeywords: " + ",".join(self.keywordList) + "\nPriority: " + str(self.priority) + "\nTranslation: " + str(self.translation) + "\n```"

        if self.destination == "Slackbot":
            sender.postToSlackbot(toSend, self.url)
        
        if self.destination == "Slack":
            sender.postToSlack(toSend, self.url)
        
        if self.destination == "Discord":
            sender.postToDiscord(toSend, self.url)




#######################################
#----- Relay Configuration Class -----#
#######################################

class Configuration:

    templateOptions = {
        "Imitation": "**{authorName}** \n{message}",
        "Imitation w/ Username": "**{authorUsername}** \n{message}",
        "Monitoring": "**A Message Has Been Sent to {channel}:** \n\n_{authorUsername}_ \n{message}",
        "Monitoring w/ Codeblocks": "**A Message Has Been Sent to {channel}:** \n\n_{authorUsername}_ \n```\n{message}\n```",
        "Jabber": "{message} \n\n#### SENT BY {authorUsername} TO {channel} @ {longTime} ####",
        "Modern w/ Username": "{message} \n\n> {longTime} - {authorUsername} TO {channel} ({server})",
        "Modern w/ Display": "{message} \n\n> {longTime} - {authorName} TO {channel} ({server})"
    }

    def __init__(
        self, 
        newUUID,
        newName,
        newDestination,
        newURL,
        newTemplate,
        newServers,
        newChannels,
        newAuthors,
        newKeywords,
        newPriority,
        newTranslator
    ):
        
        self.UUID = newUUID
        self.name = newName
        self.destination = newDestination
        self.URL = newURL
        self.template = newTemplate
        self.servers = newServers
        self.channels = newChannels
        self.authors = newAuthors
        self.keywords = newKeywords
        self.priority = newPriority
        self.translator = newTranslator
        
        
    def checkServer(self, testServer):
    
        if testServer.lower() in self.servers or not self.servers:
        
            return True
            
        else:
        
            return False
            
    
    def checkChannel(self, testChannel):
    
        if testChannel.lower() in self.channels or not self.channels:
        
            return True
            
        else:
        
            return False
            
    
    def checkAuthor(self, testAuthor):
    
        if testAuthor.lower() in self.authors or not self.authors:
        
            return True
            
        else:
        
            return False
            
    
    def checkKeywords(self, messageText):
        
        if not self.keywords:
        
            return True
        
        words = []
        
        cleanMessage = messageText.replace("\r", "").lower()
        
        lines = cleanMessage.split("\n")
        
        for eachLine in lines:
        
            lineWords = eachLine.split(" ")
            
            for eachWord in lineWords:
            
                words.append(eachWord)
                
                cleanWord = re.sub("[^A-Za-z0-9]+", "", eachWord)
                
                if cleanWord != eachWord:
                    
                    words.append(cleanWord)
                
        for eachKeyword in self.keywords:
        
            if eachKeyword in words:
            
                return True
                
        return False
        
    
    def checkPriority(self, alreadySent):
    
        if self.priority == -1 or alreadySent <= self.priority:
        
            return True
            
        else:
        
            return False
            
            
    def checkToPost(self, testServer, testChannel, testAuthor, messageText, alreadySent):
    
        if (
            self.checkServer(testServer)
            and self.checkChannel(testChannel)
            and self.checkAuthor(testAuthor)
            and self.checkKeywords(messageText)
            and self.checkPriority(alreadySent)
        ):
        
            return True
        
        else:
        
            return False
            
            
    def getTemplate(self, requestedTemplate):
        
        return self.templateOptions[requestedTemplate]
        
        
    def cleanupMessage(self, messageText):
    
        cleanMessage = messageText.replace("\r", "")
    
        if self.destination == "Slackbot":
        
            cleanMessage = cleanMessage.replace("@everyone", "@channel")
            cleanMessage = cleanMessage.replace("**", "*")
        
        if self.destination == "Slack":
        
            cleanMessage = cleanMessage.replace("@everyone", "<!channel>")
            cleanMessage = cleanMessage.replace("@here", "<!here>")
            cleanMessage = cleanMessage.replace("**", "*")
        
        return cleanMessage
        
    def translateMessage(self, messageText, baseTranslationURL, translationAPIKey):
        totalErrors = 0 
        
        authTuple = ("apikey", translationAPIKey)
        headerData = {"Content-Type": "application/json"}
        translatorURL = baseTranslationURL + "/v3/translate?version=2018-05-01"
        
        splitMessage = messageText.split("\n")
        translationData = json.dumps({"text": splitMessage, "model_id": self.translator})
        
        while True:
            translationCall = requests.post(translatorURL, data=translationData, headers=headerData, auth=authTuple)
        
            if translationCall.status_code == requests.codes.ok:
                
                translationResponse = json.loads(translationCall.text)
                translatedMessage = "\n".join([eachLine["translation"] for eachLine in translationResponse["translations"]])
                
                return translatedMessage
                
            else:
                totalErrors += 1

                print("Error Getting Translation With Status Code " + str(translationCall.status_code) + " - Trying Again")

                time.sleep(1)
                            
                if totalErrors == 3:
                    print("Tried and failed to get a translation.")

                    return messageText
        
    def sendMessage(self, messageTime, messageShortTime, messageUsername, messageName, messageServer, messageChannel, messageContent, baseTranslationURL = None, translationAPIKey = None):
    
        if self.translator is not None and baseTranslationURL is not None and translationAPIKey is not None:
            
            messageContent = self.translateMessage(messageContent, baseTranslationURL, translationAPIKey)
    
        template = self.getTemplate(self.template)
        
        relayDraft = template.format(
            longTime=messageTime, 
            shortTime=messageShortTime, 
            authorUsername=messageUsername, 
            authorName=messageName, 
            server=messageServer, 
            channel=messageChannel, 
            message=messageContent
        )
        
        toRelay = self.cleanupMessage(relayDraft)
        
        senderFunction = sender.getSender(self.destination)
        
        if senderFunction(toRelay, self.URL):
        
            print("[" + time.strftime("%d %B - %H:%M:%S UTC") + "] Message relayed to " + self.name + ".")
        