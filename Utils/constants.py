import json_helper

TOKENS = json_helper.get_db("Utils/tokens.json")

headers = {"Authorization":"Bot {}".format(TOKENS["token"]),
	"User-Agent":"SwapBot (https://www.regexr.tech, v0.1)",
	"Content-Type":"application/json"}

baseURL = "https://discordapp.com/api/channels/{}/messages"
reservationURL = baseURL.format(TOKENS["channels"]["reservations"])
emojiURL = reservationURL + "/{}/reactions/{}?limit={}&after={}"
ordersURL = baseURL.format(TOKENS["channels"]["orders"])

