import urllib

def encode_emoji(emoji):
	return urllib.urlencode({'a': emoji.encode('utf-8')}).split("=")[1]
