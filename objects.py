import time
import re

import sender

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
        newPriority
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
        
        
    def sendMessage(self, messageTime, messageShortTime, messageUsername, messageName, messageServer, messageChannel, messageContent):
    
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
        