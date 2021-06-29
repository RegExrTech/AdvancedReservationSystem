import sys
sys.path.insert(0, 'OrderTaker')
sys.path.insert(0, 'Utils')
import time
import urllib
import requests

from order_taker import get_all_messages
import json_helper
from emoji import encode_emoji
import constants

SCRAPE_LIMIT = 100

f = open("ReactionSeeder/listing_ids.txt", "r")
listing_ids = set(f.read().splitlines())
f.close()

TOKENS = constants.TOKENS

def add_reation(channel_id, message_id, emoji_id):
	url = "https://discordapp.com/api/channels/{}/messages/{}/reactions/{}/@me".format(channel_id, message_id, emoji_id)
	r = requests.put(url, headers=constants.headers)
	time.sleep(0.5)

for message in get_all_messages(SCRAPE_LIMIT):
	message_id = message['id']
	message_lines = message['content'].splitlines()
	for message_line in message_lines:
		if message_line and message_id not in listing_ids:
			encoded_emoji = encode_emoji(message_line[0])
			add_reation(TOKENS["channels"]["reservations"], message_id, encoded_emoji)
	listing_ids.add(message_id)

f = open("ReactionSeeder/listing_ids.txt", "w")
f.write("\n".join(list(listing_ids)))
f.close()


