import sys
sys.path.insert(0, 'Utils')
import requests
import json

import json_helper
import constants
import discord_helper

users = json_helper.get_db("RoleRewarder/users.json")

TOKENS = constants.TOKENS

THRESHOLD = 8

baseURL = "https://discordapp.com/api/channels/{}/messages"
scrapeURL = baseURL.format(TOKENS["channels"]["levels"])
welcomeURL = baseURL.format(TOKENS["channels"]["welcome"])
roleAssignmentURL = "https://discordapp.com/api/guilds/" + TOKENS['server_id'] + "/members/{}/roles/" + TOKENS['role_id']

messages = discord_helper.send_request(discord_helper.GET, scrapeURL, constants.headers).json()
for message in messages:
	user_id = message['mentions'][0]['id']
	level = int(message['content'].split("level ")[1].split("!")[0])
	username = message['mentions'][0]['username']
	if user_id != '333321993036365826':
		continue
	if level >= THRESHOLD and user_id not in users['active']:
		users['active'].append(user_id)
		discord_helper.send_request(discord_helper.PUT, roleAssignmentURL.format(user_id), constants.headers)
		message_data = {'content': "Welcome to the VIP section of the server, <@"+user_id+">! Please read the rules and important information in <#846468963436331088> before participating. Thank you and enjoy!"}
		discord_helper.send_request(discord_helper.POST, welcomeURL, constants.headers, json.dumps(message_data))

	json_helper.dump(users, "RoleRewarder/users.json")
