test = [
	"IGN:username SERVER:servername",
	"ign:username server:servername",
	"IGN:username\nServer:servername",
	"IGN:username\nServer: servername",
	"IGN : username Server:servername",
	"IGN : username Server : servername",
	"IGN : username Server :servername",
	"IGN: Server:servername",
	"IGN:username Server:",
	"IGN:username Server :",
	"username\nServer:servername",
	"username\nServer:servername",
	"username servername",
	"Server: servername\nIGN:username",
	"Server : servername username",
	"Server :servername IGN :username",
	"Server :servername IGN: username",
	"Server :servername IGN : username",
	"Server\t:servername\tIGN\n:username",
	"Server\t:servername\tIGN\n:username",
	"Server\t:servername\tIGN:",
	"Server\t:servername\tIGN :"
]

def ParseIGNServer(msg):
	ret = ['', '']

	#split on tab, newline, and space
	msg = msg.split()

	#try to find matches
	fieldflag = -1
	pos = 0
	while pos < len(msg):
		curentry = msg[pos].lower()
		if curentry.startswith("server") and (fieldflag == 1):
			ret[fieldflag] += f' {msg[pos]}'
		elif curentry.startswith("ign") or curentry.startswith("server") or curentry.startswith("in-game-name"):
    			#flag what we are looking at, ign or server
			if curentry.startswith("ign") or curentry.startswith("in-game-name"):
				fieldflag = 0
			else:
				fieldflag = 1

			#if a : exists in this entry then see if the name/server is after it
			if ":" in curentry:
				#split on colon and see if we have anything after it, use msg[pos] so we don't have
				#the lower version of a name or server
				colonsplit = msg[pos].split(":")

				#if something is after the colon then get it as they did name:val
				if len(colonsplit) != 2:
					#we got more than 2 entries, too many colons, fail
					return None

				#see if anything exists after the colon
				if len(colonsplit[1]):
					ret[fieldflag] = colonsplit[1]
				else:
					#nothing after the colon, see if we have another entry after us
					#in the list as it should be the value we want
					#but if no more entries exist then fail the parse
					if pos+1 >= len(msg):
						return None

					#get the next entry and skip past it in the for loop
					ret[fieldflag] = msg[pos+1]
					pos = pos + 1
			else:
				#colon should be next entry, make sure we have an entry to parse
				if pos+1 >= len(msg):
					return None

				#if the message is a colon then we should have another field after it			
				if msg[pos+1] == ":":
					#see if another field exists allowing for name : value
					#fail if no more entries exist, example inputting name :
					if pos+2 >= len(msg):
						return None

					#found colon by itself, entry after should be the value we want
					#adjust pos so we skip past it in our search
					ret[fieldflag] = msg[pos + 2]
					pos = pos + 2
				elif msg[pos+1][0] == ":":
					#starts with a :, rest should be the entry we want, double check no extra : exists in it
					if ":" in msg[pos+1][1:]:
						return None

					#no extra :, get everything after the colon
					ret[fieldflag] = msg[pos+1][1:]
				else:
					#could not find the :
					return None
		else:
			if fieldflag == -1:
				return None
			ret[fieldflag] += f' {msg[pos]}'	
			
		#next entry
		pos = pos + 1

	#make sure both fields are filled in
	if len(ret[0]) == 0 or len(ret[1]) == 0:
		return None

	return (ret[0], ret[1])
'''
for entry in test:
	print(f"Testing:\n{entry}")
	ret = ParseIGNServer(entry)
	if ret == None:
		print("Failed to parse\n")
	else:
		print(f"found User: {ret[0]} Server: {ret[1]}\n")
'''