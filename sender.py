import requests
import json
import time

def postToSlackbot(message, URL):
    totalErrors = 0

    while True:
        toPost = requests.post(URL, data=message.encode("utf-8"), headers={"Content-Type": "text/plain", "charset": "UTF-8"})
    
        if toPost.status_code == requests.codes.ok:
            return True
            
        else:
            totalErrors += 1

            print("Error Sending Slack Message With Status Code " + str(toPost.status_code) + " - Trying Again")

            time.sleep(1)
                        
            if totalErrors == 10:
                print("Tried and failed to send slack message 10 times.")

                return False
    
def postToSlack(message, URL):
    totalErrors = 0
    
    slack_data = {"text" : message}

    while True:
        toPost = requests.post(URL, data=json.dumps(slack_data), headers={"Content-Type" : "application/json"})
    
        if toPost.status_code == requests.codes.ok:
            return True
            
        else:
            totalErrors += 1

            print("Error Sending Slack Message With Status Code " + str(toPost.status_code) + " - Trying Again")

            time.sleep(1)
                        
            if totalErrors == 10:
                print("Tried and failed to send slack message 10 times.")

                return False
    
def postToDiscord(message, URL):
    totalErrors = 0
    
    discord_data = {"content" : message}
    
    while True:
        toPost = requests.post(URL, data=discord_data)
        
        if toPost.status_code == requests.codes.ok or toPost.status_code == 204:
            return True
            
        else:
            totalErrors += 1

            print("Error Sending Discord Message With Status Code " + str(toPost.status_code) + " - Trying Again")

            time.sleep(1)
                        
            if totalErrors == 10:
                print("Tried and failed to send discord message 10 times.")

                return False
                
def getSender(senderType):

    senders = {
        "Slackbot": postToSlackbot,
        "Slack": postToSlack,
        "Discord": postToDiscord
    }
    
    return senders[senderType]