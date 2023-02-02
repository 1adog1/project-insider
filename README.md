# Project Insider

Project Insider is a tool for relaying messages from discord to other discord servers, and even other platforms. It boasts a simple text interface to configure multiple relays, and a log of relay activity.

## Requirements
* Python ≥ 3.11
  * [requests](https://pypi.org/project/requests/)
  * [discord.py](https://pypi.org/project/discord.py/)
  * [tabulate](https://pypi.org/project/tabulate/)
  
## Compatible Platforms
* Discord Webhook
* Slack App Webhook
* Remote Slackbot Webhook
  * This is a lesser known bot in which you literally take over Slack's Default Bot for a server. More info can be found on the bot's [App Page](https://slack.com/apps/A0F81R8ET-slackbot).
  
## Getting Started

Before starting the relay, make sure you do the following:
* Setup a Discord App and add a Bot to it.
* Run `manager.py` to get the initial setup done. 
  * All future changes to your relay can be made using this program. Type `HELP` for a full list of commands.
* Once you've finished the initial setup, just run `relay.py`.
  * `relay.py` only needs to be restarted if you change your Discord App ClientID or Bot Token. All other changes will automatically take effect when the relay processes its next message.