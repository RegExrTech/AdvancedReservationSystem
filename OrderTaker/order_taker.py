import sys
sys.path.insert(0, 'Utils')
import time
import urllib
import requests
import json_helper
import json
from collections import defaultdict
from emoji import encode_emoji
import constants
import discord_helper

reservations = json_helper.get_db("OrderTaker/reservations.json")

TOKENS = constants.TOKENS

baseURL = "https://discordapp.com/api/channels/{}/messages"
reservationURL = baseURL.format(TOKENS["channels"]["reservations"])
emojiURL = reservationURL + "/{}/reactions/{}?limit={}&after={}"
ordersURL = baseURL.format(TOKENS["channels"]["orders"])
bot_id = TOKENS['bot_id']
admin_id = TOKENS['admin_id']

SCRAPE_LIMIT = 100


def get_all_messages(message_scrape_limit):
	messages = discord_helper.send_request(discord_helper.GET, reservationURL+"?limit="+str(message_scrape_limit), constants.headers).json()
	all_messages = [x for x in messages]

	while len(messages) > 0 and len(all_messages) % message_scrape_limit == 0:
		before = min([int(x['id']) for x in messages])
		messages = discord_helper.send_request(discord_helper.GET, reservationURL+"?limit="+str(message_scrape_limit)+"&before="+str(before), constants.headers).json()
		all_messages += messages
	return all_messages

def get_reactions_from_message(message, reaction_scrape_limit):
	d = {}  # Emoji to user list
	for reaction in message['reactions']:
		raw_emoji = reaction['emoji']['name']
		url_encoded_reaction = encode_emoji(raw_emoji)
		reaction_users = discord_helper.send_request(discord_helper.GET, emojiURL.format(message['id'], url_encoded_reaction, reaction_scrape_limit, "").split("&")[0], constants.headers).json()
		all_reaction_users = [x for x in reaction_users]
		while len(reaction_users) > 0 and len(all_reaction_users) % reaction_scrape_limit == 0:
			after = max([x['id'] for x in reaction_users])
			reaction_users = discord_helper.send_request(discord_helper.GET, emojiURL.format(message['id'], url_encoded_reaction, reaction_scrape_limit, after), constants.headers).json()
			all_reaction_users += reaction_users
		d[raw_emoji] = [x['id'] for x in all_reaction_users if not x['id'] == bot_id]
	return d

def main():
	new_reservations = defaultdict(lambda: [])
	for message in get_all_messages(SCRAPE_LIMIT):
		message_id = message['id']
		reactions = get_reactions_from_message(message, SCRAPE_LIMIT)
		for message_line in message['content'].splitlines():
			for reaction in reactions:
				if reaction not in message_line:
					continue
				for user_id in reactions[reaction]:
					if user_id == bot_id:
						continue
					if user_id not in reservations:
						reservations[user_id] = {}
					if message_id not in reservations[user_id]:
						reservations[user_id][message_id] = []
					product = message_line.split(reaction)[1].strip()
					if product not in reservations[user_id][message_id]:
						reservations[user_id][message_id].append(product)
						new_reservations[user_id].append(product)

	new_order_text_base = "New orders have been found, <@" + admin_id + ">!\n-------------------\n"
	new_order_text = new_order_text_base

	for user_id in new_reservations:
		user_order_text = "<@"+user_id+">\n\n"
		for product in new_reservations[user_id]:
			user_order_text += "* " + product + "\n"
		user_order_text += "\n-------------------\n"
		if len(new_order_text + user_order_text) < 2000:
			new_order_text = new_order_text + user_order_text

	if new_order_text != new_order_text_base:
		discord_helper.send_request(discord_helper.POST, ordersURL, constants.headers, json.dumps({'content': new_order_text}))
	json_helper.dump(reservations, "OrderTaker/reservations.json")

if __name__ == "__main__":
	main()
