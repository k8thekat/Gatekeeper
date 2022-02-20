'''
   Copyright (C) 2021-2022 Katelynn Cadwallader.

   This file is part of Gatekeeper, the AMP Minecraft Discord Bot.

   Gatekeeper is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.

   Gatekeeper is distributed in the hope that it will be useful, but WITHOUT
   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
   License for more details.

   You should have received a copy of the GNU General Public License
   along with Gatekeeper; see the file COPYING.  If not, write to the Free
   Software Foundation, 51 Franklin Street - Fifth Floor, Boston, MA
   02110-1301, USA. 

'''
import sqlite3
import os, sys
import datetime
import json
import time

db = None

def dump_to_json(data):
	for entry in data:
		if type(data[entry]) == datetime.datetime:
			data[entry] = data[entry].isoformat()
		elif type(data[entry]) == bool:
			data[entry] = int(data[entry])
	return json.dumps(data)

class Database:
	def __init__(self):
		DBExists = False
		if os.path.exists("Gatekeeper.db"):
			DBExists = True

		self._db = sqlite3.connect("Gatekeeper.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
		self._db.row_factory = sqlite3.Row
		if not DBExists:
			self._InitializeDatabase()
			self._InitializeDefaultData()

	def _InitializeDatabase(self):
		cur = self._db.cursor()
		cur.execute("""create table Roles (
						ID integer primary key,
						DiscordID text not null collate nocase unique
						)""")

		cur.execute("""create table Permissions (
						ID integer primary key,
						Name text not null collate nocase,
						Description text
						)""")

		cur.execute("""create table RolePermissions (
						RoleID integer not null,
						PermissionID integer not null,
						foreign key(RoleID) references Roles(ID),
						foreign key(PermissionID) references Permissions(ID),
						unique(RoleID, PermissionID)
						)""")

		cur.execute("""create table Servers (
						ID integer primary key,
						InstanceID text not null unique collate nocase,
						FriendlyName text unique collate nocase,
						Whitelist integer not null,
						Donator integer not null,
						MapCreationDate timestamp,
						UserLimit integer,
						DiscordConsoleChannel text nocase,
						DiscordChatChannel text nocase,
						DiscordRole text collate nocase
						)""")

		cur.execute("""create table ServerNicknames (
						ID integer primary key,
						ServerID integer not null,
						Nickname text not null unique collate nocase,
						foreign key(ServerID) references Servers(ID)
						)""")

		cur.execute("""create table Users (
						ID integer primary key,
						DiscordID text not null unique collate nocase,
						DiscordName text collate nocase,
						IngameName text collate nocase,
						UUID text unique collate nocase,
						GlobalBanExpiration timestamp,
						Donator integer not null,
						ServerModerator integer not null
						)""")

		cur.execute("""create table ServerUsers (
						ID integer primary key,
						ServerID integer not null,
						UserID integer not null,
						Whitelisted integer not null,
						LastLogin timestamp,
						TimePlayed integer,
						SuspensionExpiration timestamp,
						foreign key(UserID) references Users(ID),
						foreign key(ServerID) references Servers(ID),
						unique(ServerID, UserID)
						)""")
						
		cur.execute("""create table UserInfractions (
						ID integer primary key,
						UserID integer not null,
						ServerID integer,
						ModID integer not null,
						Note text not null,
						InfractionDate timestamp default (datetime('now')),
						foreign key(UserID) references Users(ID),
						foreign key(ServerID) references Servers(ID),
						foreign key(ModID) references Users(ID)
						)""")

		cur.execute("""create table Log (
						ID integer primary key,
						Log text not null,
						LogDate timestamp default (datetime('now'))
						)""")

		cur.execute("""create table Config (
						ID integer primary key,
						Name text not null unique,
						Value text
						)""")

		self._db.commit()

	def _InitializeDefaultData(self):
		"""
		cur = self._db.cursor()
		cur.execute("insert into Permissions(Name, Description) values('Kick', 'Ability to kick users')")
		cur.execute("insert into Permissions(Name, Description) values('Ban', 'Ability to ban users')")
		cur.execute("insert into Permissions(Name, Description) values('Whitelist', 'Ability to whitelist users')")
		cur.execute("insert into Permissions(Name, Description) values('Warn', 'Ability to warn users')")
		cur.execute("insert into Permissions(Name, Description) values('Restart', 'Ability to restart users')")
		cur.execute("insert into Permissions(Name, Description) values('ServerConsole', 'Ability to run console commands')")
		cur.close()
		self._db.commit()
		"""
		return

	def _execute(self, SQL, params):
		Retry = 0

		while(1):
			try:
				cur = self._db.cursor()
				cur.execute(SQL, params)
				cur.close()
				self._db.commit()
				return

			except sqlite3.OperationalError as ex:
				#if locked then try up to 3 times before bailing
				if Retry == 3:
					raise Exception(ex)
				Retry += 1
				time.sleep(0.1)
				continue

			except Exception as ex:
				raise Exception(ex)

	def _fetchone(self, SQL, params):
		cur = self._db.cursor()
		cur.execute(SQL, params)
		return (cur.fetchone(), cur)

	def _fetchall(self, SQL, params):
		cur = self._db.cursor()
		cur.execute(SQL, params)
		return (cur.fetchall(), cur)

	def _logdata(self, data):
		self._execute("insert into log(log) values(?)", (data,))

	def _UpdateServer(self, dbserver, **args):
		#get the property to update
		entry = list(args.keys())[0]
		self._execute(f"Update servers set {entry}=? where ID=?", (args[entry],dbserver.ID))
		jdata = dump_to_json({"Type": "ServerUpdate", "ServerID": dbserver.ID, "Field": entry, "Value": args[entry]})
		self._logdata(jdata)

	def _UpdateUser(self, dbuser, **args):
		#get the property to update
		entry = list(args.keys())[0]
		self._execute(f"Update users set {entry}=? where ID=?", (args[entry], dbuser.ID))
		jdata = dump_to_json({"Type": "UserUpdate", "UserID": dbuser.ID, "Field": entry, "Value": args[entry]})
		self._logdata(jdata)

	def _UpdateServerUser(self, dbserveruser, **args):
		#get the property to update
		entry = list(args.keys())[0]
		self._execute(f"Update serverusers set {entry}=? where ID=?", (args[entry], dbserveruser.ID))
		jdata = dump_to_json({"Type": "ServerUserUpdate", "ServerID": dbserveruser.GetServer().ID, "UserID": dbserveruser.GetUser().ID, "Field": entry, "Value": args[entry]})
		self._logdata(jdata)

	def AddPermission(self, Name:str, Description:str=None):
		Name = Name.capitalize().replace(" ", "_")
		self._execute(f"Insert into Permissions(Name, Description) Values(?, ?)", (Name, Description))
		jdata = dump_to_json({"Type": "AddPermission", "Name": Name, "Description": Description})
		self._logdata(jdata)

	def UpdatePermission(self, Name:str, NewDescription:str):
		Name = Name.capitalize().replace(" ", "_")
		self._execute(f"Update Permissions set Description=? where Name=?", (NewDescription, Name))
		jdata = dump_to_json({"Type": "UpdatePermission", "Name": Name, "Description": NewDescription})
		self._logdata(jdata)

	def GetPermissionDescription(self, Name:str):
		Name = Name.capitalize().replace(" ", "_")
		row = self._fetchone(f"Select Description from Permissions where Name=?", (Name, ))
		if row:
			return row["Description"]
		return None

	def AddRole(self, DiscordID:str):
		return DBRole(db=self, DiscordID=DiscordID)

	def GetRole(self, DiscordID:str):
		#we need to look for a server where the friendly name or nickname matches the provided name
		(row, cur) = self._fetchone(f"select ID from Roles where DiscordID=?", (int(DiscordID),))

		#if no rows then fail
		if not row:
			cur.close()
			return None

		ret = DBRole(db=self, ID=int(row["id"]))
		cur.close()
		return ret

	def DeleteRole(self, dbrole):
		self._execute("Delete from RolePermissions where RoleID=?", (dbrole.ID,))
		self._execute("Delete from Roles where ID=?", (dbrole.ID,))
		jdata = dump_to_json({"Type": "DeleteRole", "DiscordID": dbrole.DiscordID})
		self._logdata(jdata)

	def _UpdateRole(self, dbrole, **args):
		#get the property to update
		entry = list(args.keys())[0]
		self._execute(f"Update Roles set {entry}=? where ID=?", (args[entry], dbrole.ID))
		jdata = dump_to_json({"Type": "UpdateRole", "Name": entry, "Value": args[entry]})
		self._logdata(jdata)

	def _UpdateRolePermission(self, dbrole, permission, value):
		#get the property to update
		if not value:
			self._execute("delete from RolePermissions where RoleID=? and PermissionID=?", (dbrole.ID, permission))
		else:
			try:
				self._execute("insert into RolePermissions (RoleID, PermissionID) values(?, ?)", (dbrole.ID, permission))
			except:
				print("had error")
				pass
		jdata = dump_to_json({"Type": "UpdateRolePermission", "Role": dbrole.DiscordID, "Permission": permission, "Value": value})
		self._logdata(jdata)
		return True

	def GetAllRoles(self):
		#return a list of roles with a certain permission
		(rows, cur) = self._fetchall("select DiscordID from Roles", ())

		RoleList = []
		for entry in rows:
			RoleList.append(DBRole(self, DiscordID=entry["DiscordID"]))

		cur.close()
		return RoleList

	def GetRolesListWithPermission(self, PermissionName:str):
		#return a list of roles with a certain permission
		(rows, cur) = self._fetchall("select Roles.DiscordID from Roles, Permissions, RolePermissions where Permissions.Name=? and RolePermissions.PermissionID = Permissions.ID and Roles.ID = RolePermissions.RoleID", (PermissionName.capitalize(),))

		RoleList = []
		for entry in rows:
			RoleList.append(int(entry["DiscordID"]))

		cur.close()
		return RoleList

	def GetRolesWithPermission(self, PermissionName:str):
		#get our list first
		RoleList = self.GetRolesListWithPermission(PermissionName)

		ret = []
		for entry in RoleList:
			ret.append(DBRole(self, DiscordID=entry))
		return ret

	def AddServer(self, InstanceID:str, FriendlyName:str=None, Whitelist:bool=False, Donator:bool=False, MapCreationDate:datetime.datetime=None, UserLimit:int=None, DiscordConsoleChannel:str=None, DiscordChatChannel:str=None, DiscordRole:str=None):
		#try:
		return DBServer(db=self, InstanceID=InstanceID, FriendlyName=FriendlyName, Whitelist=Whitelist, Donator=Donator, MapCreationDate=MapCreationDate, UserLimit=UserLimit, DiscordConsoleChannel=DiscordConsoleChannel, DiscordChatChannel=DiscordChatChannel, DiscordRole=DiscordRole)
		#except:
			#return None

	def GetServer(self, InstanceID:str=None, Name:str=None):
		if not InstanceID and not Name:
			return None
	
		#we need to look for a server where the friendly name or nickname matches the provided name
		if InstanceID:
			(row, cur) = self._fetchone(f"select ID from Servers where InstanceID=?", (InstanceID,))
		else:
			(row, cur) = self._fetchone(f"select ID from Servers where FriendlyName=?", (Name,))

		#if no rows then try nicknames
		if not row:
			if Name:
				cur.close()
				(row, cur) = self._fetchone(f"select ServerID as ID from ServerNicknames where Nickname=?", (Name,))

			if not row:
				cur.close()
				return None

		#create a new user to return and let the object populate itself
		ret = DBServer(ID=int(row["ID"]), db=self)

		cur.close()
		return ret

	def GetServerUser(self, dbserver, dbuser):
		#we need to look for a server where the friendly name or nickname matches the provided name
		(row, cur) = self._fetchone(f"select ID from ServerUsers where ServerID=? and UserID=?", (dbserver.ID, dbuser.ID))
		#if no rows then fail
		if not row:
			return None

		#create a new serveruser object and return it
		ret = DBServerUser(ID=int(row["ID"]), Server=dbserver, User=dbuser, db=self)

		cur.close()
		return ret

	def GetUser(self, value:str):
		#find the user
		(row, cur) = self._fetchone(f"select ID from Users where DiscordID=? or DiscordName=? or IngameName=? or UUID=?", (value,value,value,value))
		if not row:
			cur.close()
			return None

		#create a new user object to return and let the object populate itself
		ret = DBUser(ID=int(row["ID"]), db=self)

		cur.close()
		return ret

	def AddUser(self, DiscordID:str=None, DiscordName:str=None, IngameName:str=None, UUID:str=None, GlobalBanExpiration:datetime.datetime=None, Donator:bool=False, ServerModerator:bool=False):
		try:
			return DBUser(db=self, DiscordID=DiscordID, DiscordName=DiscordName, IngameName=IngameName, UUID=UUID, GlobalBanExpiration=GlobalBanExpiration, Donator=Donator, ServerModerator=ServerModerator)
		except Exception as e:
			print(e)
			return None

	def GetAllUsers(self, GlobalBanExpiration=None, Donator=None, ServerModerator=None):
		#get all servers that we are on
		SQL = "Select ID from Users"
		SQLWhere = []
		SQLArgs = []

		if(GlobalBanExpiration):
			SQLWhere.append("GlobalBanExpiration <= ?")
			SQLArgs.append(GlobalBanExpiration)
		if(Donator):
			SQLWhere.append("and Donator = ?")
			SQLArgs.append(Donator)
		if(ServerModerator):
			SQLWhere.append("ServerModerator = ?")
			SQLArgs.append(ServerModerator)

		if len(SQLWhere):
			SQL = SQL + " where " + " and ".join(SQLWhere)

		(rows, cur) = self._fetchall(SQL, tuple(SQLArgs))
		ret = []
		for entry in rows:
			User = DBUser(self, ID=entry["ID"])
			ret.append(User)

		cur.close()
		return ret

	def _AddConfig(self, Name, Value):
		self._execute("Insert into config(Name, Value) values(?, ?)", (Name, Value))
		(ret, cur) = self._fetchone("Select ID from Config where Name=?", (Name,))
		if not ret:
			return None
		ID = int(ret["ID"])
		cur.close()
		jdata = dump_to_json({"Type": "AddConfig", "Name": Name, "Value": Value})
		self._logdata(jdata)
		return ID

	def GetConfig(self):
		return DBConfig(self)

	def _DeleteConfig(self, ConfigID, ConfigName):
		self._execute("Delete from Config where ID=?", (ConfigID,))
		jdata = dump_to_json({"Type": "DeleteConfig", "Name": ConfigName})
		self._logdata(jdata)

	def _UpdateConfig(self, ID, Name, Value):
		self._execute("Update Config set Value=? where ID=?", (Value, ID))
		jdata = dump_to_json({"Type": "UpdateConfig", "Name": Name, "Value": Value})
		self._logdata(jdata)

	def GetLog(self, AfterTime:datetime.datetime=None, BeforeTime:datetime.datetime=None, StartingID:int=None, Limit:int=100):
		SQL = "Select L.ID, L.Log, L.LogDate from Log L"
		Params = []
		if StartingID or AfterTime or BeforeTime:
			NeedAND = False
			SQL += " Where "
			if StartingID:
				SQL += " L.ID >= ? "
				Params.append(StartingID)
				NeedAND = True
			if AfterTime:
				if NeedAND:
					SQL += " and "
				SQL += " L.LogDate > "
				Params.append(AfterTime)
				NeedAND = True
			if BeforeTime:
				if NeedAND:
					SQL += " and "
				SQL += " L.LogDate < "
				Params.append(BeforeTime)
				NeedAND = True
		SQL += " order by L.LogDate "
		if Limit:
			SQL += " Limit ?"
			Params.append(Limit)

		NeededUsers = []
		NeededServers = []
		(rows, cur) = self._fetchall(SQL, tuple(Params))
		ret = []
		for entry in rows:
			logentry = {}
			logentry["ID"] = entry["ID"]
			logentry["Log"] = json.loads(entry["Log"])
			logentry["Date"] = entry["LogDate"]
			ret.append(logentry)

			#if we have a userid, serverid, or modid in the log json then store it as needed
			if ("UserID" in logentry["Log"]) and (logentry["Log"]["UserID"] not in NeededUsers):
				NeededUsers.append(logentry["Log"]["UserID"])
			if ("ModID" in logentry["Log"]) and (logentry["Log"]["ModID"] not in NeededUsers):
				NeededUsers.append(logentry["Log"]["ModID"])
			if ("ServerID" in logentry["Log"]) and (logentry["Log"]["ServerID"] not in NeededServers):
				NeededServers.append(logentry["Log"]["ServerID"])

		cur.close()

		#go get all of the users to fill in
		Users = {}
		while len(NeededUsers):
			Count = len(NeededUsers)
			if len(NeededUsers) > 50:
				Count = 50
			qentries = ("?,"*Count)[:-1]
			Params = tuple(NeededUsers[0:Count])
			NeededUsers = NeededUsers[Count:]
			(rows, cur) = self._fetchall(f"Select ID, DiscordID, DiscordName, IngameName, UUID from Users where ID in ({qentries})", tuple(Params))
			for entry in rows:
				Users[int(entry["ID"])] = {"DiscordID": int(entry["DiscordID"]), "DiscordName": entry["DiscordName"], "IngameName": entry["IngameName"], "UUID": entry["UUID"]}
			cur.close()

		#get servers
		Servers = {}
		while len(NeededServers):
			Count = len(NeededServers)
			if len(NeededServers) > 50:
				Count = 50
			qentries = ("?,"*Count)[:-1]
			Params = tuple(NeededServers[0:Count])
			NeededServers = NeededServers[Count:]
			(rows, cur) = self._fetchall(f"Select ID, FriendlyName from Servers where ID in ({qentries})", tuple(Params))
			for entry in rows:
				Servers[int(entry["ID"])] = entry["FriendlyName"]
			cur.close()

		#now update all log entries
		for entry in ret:
			if "UserID" in entry["Log"]:
				UID = int(entry["Log"]["UserID"])
				if UID in Users:
					entry["Log"].pop("UserID")
					entry["Log"]["User_DiscordID"] = int(Users[UID]["DiscordID"])
					entry["Log"]["User_DiscordName"] = Users[UID]["DiscordName"]
					entry["Log"]["User_IngameName"] = Users[UID]["IngameName"]
			if "ModID" in entry["Log"]:
				MID = int(entry["Log"]["ModID"])
				if MID in Users:
					entry["Log"].pop("ModID")
					entry["Log"]["Mod_DiscordID"] = int(Users[MID]["DiscordID"])
					entry["Log"]["Mod_DiscordName"] = Users[MID]["DiscordName"]
					entry["Log"]["Mod_IngameName"] = Users[MID]["IngameName"]
			if "ServerID" in entry["Log"]:
				if entry["Log"]["ServerID"] in Servers:
					entry["Log"]["Server"] = Servers[int(entry["Log"]["ServerID"])]
					entry["Log"].pop("ServerID")

		return ret

class DBUser:
	def __init__(self, db:Database, ID:int=None, DiscordID:str=None, DiscordName:str=None, IngameName:str=None, UUID:str=None, GlobalBanExpiration:datetime.datetime=None, Donator:bool=False, ServerModerator:bool=False):
		#set defaults
		Params = locals()
		Params.pop("self")
		Params.pop("db")
		Params.pop("__class__")
		super().__setattr__("_db", db)
		for entry in Params:
			super().__setattr__(entry, Params[entry])

		if((GlobalBanExpiration != None) and (type(GlobalBanExpiration) != datetime.datetime)):
			raise Exception("GlobalBanExpiration is not datetime")

		#if given a database and ID then look up our values
		if ID:
			(row, cur) = self._db._fetchone("Select * From Users where ID=?", (ID,))
			if row:
				for entry in row.keys():
					super().__setattr__(entry, row[entry])
			else:
				raise Exception(f"Unable to locate User ID {ID}")
			cur.close()
			super().__setattr__("ID", int(self.ID))
			super().__setattr__("DiscordID", int(self.DiscordID))
		else:
			#we should have a discord id
			if not DiscordID or (not len(DiscordID)):
				raise Exception("Missing discord ID on new user")

			#add user to the database
			DBFields = Params

			#create the sql line
			SQL = "insert into users ("
			SQLVars = []

			for entry in DBFields:
				if DBFields[entry] != None:
					SQL += entry + ","
					SQLVars.append(DBFields[entry])

			SQL = SQL[:-1] + ") values (" + ("?,"*len(SQLVars))[:-1] + ")"
			#create the tuple needed
			SQLTuple = tuple(SQLVars)
			
			#execute it
			self._db._execute(SQL, SQLTuple)

			#now find the ID
			(row, cur) = self._db._fetchone("Select ID From Users where DiscordID=?", (DiscordID,))
			if row:
				super().__setattr__("ID", int(row["ID"]))
			else:
				raise Exception(f"Unable to locate new user with Discord ID {DiscordID}")
			cur.close()

			jdata = dump_to_json({"Type": "AddUser", "UserID": self.ID})
			self._db._logdata(jdata)

	def __setattr__(self, name: str, value):
		if (name == "ID") or (name[0] == "_"):
			return
		elif name == "GlobalBanExpiration":
			#make sure proper value
			if (type(value) != datetime.datetime) and (type(value) != None):
				raise Exception("Invalid type")
		elif name in ["Donator", "ServerModerator"]:
			#conver to bool
			value = bool(value)
		elif name == "DiscordID":
			#conver to int
			value =int(value)

		#set value and update the user
		super().__setattr__(name, value)
		self._db._UpdateUser(self, **{name:value})

	def AddInfraction(self, server, mod, note):
		if server != None:
			ServerID = server.ID
		else:
			ServerID = None
		self._db._execute("Insert into UserInfractions (ServerID, UserID, ModID, Note) values(?, ?, ?, ?)", (ServerID, self.ID, mod.ID, note))
		jdata = dump_to_json({"Type": "AddUserInfraction", "ServerID": ServerID, "UserID": self.ID, "ModID": mod.ID})
		self._db._logdata(jdata)

	def DelInfraction(self, ID):
		self._db._execute("Delete from UserInfractions where ID=? and UserID=?", (ID, self.ID))

	@property
	def Infractions(self):
		#get all of our infractions and return them in a list of dictionary entries
		(rows, cur) = self._db._fetchall("""
			Select UI.ID, S.FriendlyName, M.DiscordID, M.DiscordName, UI.Note, UI.InfractionDate
			from UserInfractions UI, Users M
			left join Servers S on UI.ServerID=S.ID
			where UI.UserID=? and M.ID=UI.ModID
			Order By UI.InfractionDate""", (self.ID,))

		ret = []
		for entry in rows:
			data = {}
			data["ID"] = int(entry["ID"])
			data["Server"] = entry["FriendlyName"]
			data["Mod_DiscordID"] = int(entry["DiscordID"])
			data["Mod_DiscordName"] = entry["DiscordName"]
			data["Note"] = entry["Note"]
			data["Date"] = entry["InfractionDate"]
			ret.append(data)

		cur.close()
		return ret

	def GetServer(self, dbserver = None, InstanceID:str = None, Name:str = None):
		if not dbserver:
			Server = self._db.GetServer(InstanceID=InstanceID, Name=Name)

		if not Server:
			return None

		#go find the entry
		return self._db.GetServerUser(Server, self)

	def GetAllServers(self):
		#get all servers that we are on
		(rows, cur) = self._db._fetchall("Select ServerID from ServerUsers where UserID=?", (self.ID,))
		ret = []
		for entry in rows:
			Server = DBServer(self._db, ID=entry["ServerID"])
			ret.append(self._db.GetServerUser(Server, self))

		cur.close()
		return ret

class DBServer:
	def __init__(self, db:Database, ID:int=None, InstanceID:str=None, FriendlyName:str=None, Whitelist:bool=False, Donator:bool=False, MapCreationDate:datetime.datetime=None, UserLimit:int=None, DiscordConsoleChannel:str=None, DiscordChatChannel:str=None, DiscordRole:str=None):
		#set defaults
		Params = locals()
		Params.pop("self")
		Params.pop("db")
		Params.pop("__class__")
		super().__setattr__("_db", db)
		for entry in Params:
			super().__setattr__(entry, Params[entry])

		if(self.ID != None):
			super().__setattr__("ID", int(self.ID))
		if(self.DiscordConsoleChannel != None):
			super().__setattr__("DiscordConsoleChannel", int(self.DiscordConsoleChannel))
		if(self.DiscordChatChannel != None):
			super().__setattr__("DiscordChatChannel", int(self.DiscordChatChannel))

		if((MapCreationDate != None) and (type(MapCreationDate) != datetime.datetime)):
			raise Exception("MapCreationDate is not datetime")

		#if given a database and ID then look up our values
		if ID:
			(row, cur) = self._db._fetchone("Select * From Servers where ID=?", (ID,))
			if row:
				for entry in row.keys():
					super().__setattr__(entry, row[entry])
			else:
				raise Exception(f"Unable to locate Server ID {ID}")
			cur.close()
		else:
			#we should have an InstanceID
			if not InstanceID or (not len(InstanceID)):
				raise Exception("Missing friendly name on server")

			#add server to the database after making sure the friendly name isn't already used as a nickname
			server = self._db.GetServer(InstanceID)
			if server:
				raise Exception("InstanceID already found")

			DBFields = Params

			#create the sql line
			SQL = "insert into Servers ("
			SQLVars = []

			for entry in DBFields:
				if DBFields[entry] != None:
					SQL += entry + ","
					SQLVars.append(DBFields[entry])

			SQL = SQL[:-1] + ") values (" + ("?,"*len(SQLVars))[:-1] + ")"
			#create the tuple needed
			SQLTuple = tuple(SQLVars)
			
			#execute it
			self._db._execute(SQL, SQLTuple)

			#now find the ID
			(row, cur) = self._db._fetchone("Select ID From Servers where InstanceID=?", (InstanceID,))
			if row:
				super().__setattr__("ID", int(row["ID"]))
			else:
				raise Exception(f"Unable to locate new server with InstanceID {InstanceID}")
			cur.close()

			jdata = dump_to_json({"Type": "AddServer", "ServerID": self.ID, "InstanceID": InstanceID})
			self._db._logdata(jdata)

	def __setattr__(self, name: str, value):
		if (name in ["ID", "Nicknames"]) or (name[0] == "_"):
			return
		elif name == "MapCreationDate":
			#make sure proper value
			if type(value) != datetime.datetime:
				raise Exception("Invalid type")
		elif name in ["Whitelist", "Donator"]:
			#conver to bool
			value = bool(value)
		elif name in ["UserLimit", "DiscordConsoleChannel", "DiscordChatChannel"]:
			value = int(value)

		#set value and update the user
		super().__setattr__(name, value)
		self._db._UpdateServer(self, **{name:value})

	@property
	def Nicknames(self):
		#get all of the nicknames for this server
		(rows, cur) = self._db._fetchall("Select Nickname from ServerNicknames where ServerID=?", (self.ID,))
		Nicknames = []
		for entry in rows:
			Nicknames.append(entry["Nickname"])

		return Nicknames

	def AddNickname(self, Nickname:str):
		try:
			self._db._execute("Insert into ServerNicknames (ServerID, Nickname) values(?,?)", (self.ID, Nickname))
			jdata = dump_to_json({"Type": "AddServerNickname", "ServerID": self.ID, "Nickname": Nickname})
			self._db._logdata(jdata)
		except:
			return False
		return True

	def RemoveNickname(self, Nickname:str):
		self._db._execute("delete from ServerNicknames where ServerID=? and Nickname=?", (self.ID, Nickname))
		jdata = dump_to_json({"Type": "DeleteServerNickname", "ServerID": self.ID, "Nickname": Nickname})
		self._db._logdata(jdata)

	def AddUser(self, dbuser:DBUser=None, DiscordID:str = None, DiscordName:str = None, IngameName:str = None, UUID:str = None):
		try:
			if not dbuser:
				dbuser = self._db.GetUser(DiscordID=DiscordID, DiscordName=DiscordName, IngameName=IngameName, UUID=UUID)
			if not dbuser:
				return None

			#make sure we don't add an already existing user
			ServerUser = self._db.GetServerUser(self, dbuser)
			if ServerUser:
				return ServerUser

			self._db._execute("Insert into ServerUsers(ServerID, UserID, Whitelisted) values(?, ?, ?)", (self.ID, dbuser.ID, False))
			jdata = dump_to_json({"Type": "AddServerUser", "ServerID": self.ID, "UserID": dbuser.ID})
			self._db._logdata(jdata)
		except:
			return None
		return self._db.GetServerUser(self, dbuser)

	def GetUser(self, Value = None):
		if type(Value) == DBUser:
			dbuser = Value
		else:
			dbuser = self._db.GetUser(Value)

		if not dbuser:
			return None

		#go find the entry
		return self._db.GetServerUser(self, dbuser)

	def GetAllUsers(self, Whitelisted=None, LastLogin=None, SuspensionExpiration=None):
		#get all servers that we are on
		SQL = "Select UserID from ServerUsers where ServerID=?"
		SQLArgs = [self.ID]
		if(Whitelisted):
			SQL += " and Whitelisted=?"
			SQLArgs.append(Whitelisted)
		if(LastLogin):
			SQL += " and LastLogin <= ?"
			SQLArgs.append(LastLogin)
		if(SuspensionExpiration):
			SQL += " and SuspensionExpiration <= ?"
			SQLArgs.append(SuspensionExpiration)

		(rows, cur) = self._db._fetchall(SQL, tuple(SQLArgs))
		ret = []
		for entry in rows:
			User = DBUser(self._db, ID=entry["UserID"])
			ret.append(self._db.GetServerUser(self, User))

		cur.close()
		return ret

	def AddUserInfraction(self, user:DBUser, mod:DBUser, note:str):
		user.AddInfraction(self, mod, note)

class DBServerUser:
	def __init__(self, db:Database, Server:DBServer, User:DBUser, ID=None, Whitelisted:bool=False, LastLogin:datetime.datetime=None,TimePlayed:int= 0, SuspensionExpiration:datetime.datetime=None):
		#set defaults
		Params = locals()
		Params.pop("self")
		Params.pop("db")
		Params.pop("__class__")
		Params.pop("Server")
		Params.pop("User")
		super().__setattr__("_db", db)
		super().__setattr__("_Server", Server)
		super().__setattr__("_User", User)
		for entry in Params:
			super().__setattr__(entry, Params[entry])

		#if given a database and ID then look up our values
		if ID:
			(row, cur) = self._db._fetchone("Select * From ServerUsers where ID=?", (ID,))
			if row:
				for entry in row.keys():
					super().__setattr__(entry, row[entry])
			else:
				raise Exception(f"Unable to locate ServerUser ID {ID}")
			cur.close()
		else:
			#add the combo to the database after making sure they don't already exist
			serveruser = self._db.GetServerUser(Server, User)
			if serveruser:
				raise Exception("Server/User already found")

			DBFields = Params

			#create the sql line
			SQL = "insert into ServerUsers (ServerID, UserID, "
			SQLVars = [Server.ID, User.ID]

			for entry in DBFields:
				if DBFields[entry] != None:
					SQL += entry + ","
					SQLVars.append(DBFields[entry])

			SQL = SQL[:-1] + ") values (" + ("?,"*len(SQLVars))[:-1] + ")"
			#create the tuple needed
			SQLTuple = tuple(SQLVars)
			
			#execute it
			self._db._execute(SQL, SQLTuple)

			#now find the ID
			(row, cur) = self._db._fetchone("Select ID From ServerUsers where ServerID=? and UserID=?", (Server.ID,User.ID))
			if row:
				super().__setattr__("ID", row["ID"])
			else:
				raise Exception(f"Unable to locate new serveruser")
			cur.close()

			jdata = dump_to_json({"Type": "AddServerUser", "ServerID": Server.ID, "UserID": User.ID})
			self._db._logdata(jdata)

	def __setattr__(self, name: str, value):
		if (name == "ID") or (name[0] == "_"):
			return
		elif name in ["LastLogin", "SuspensionExpiration"]:
			#make sure proper value
			if type(value) != datetime.datetime:
				raise Exception("Invalid type")
		elif name == "Whitelisted":
			#conver to bool
			value = bool(value)
		elif name == "TimePlayed":
			#conver to integer
			value = int(value)

		#set value and update the user
		super().__setattr__(name, value)
		self._db._UpdateServerUser(self, **{name:value})

	def GetServer(self):
		return self._Server

	def GetUser(self):
		return self._User

class DBRole:
	def __init__(self, db:Database=None, ID:int=None, DiscordID:str=None):
		#set defaults
		Params = locals()
		Params.pop("self")
		Params.pop("db")
		super().__setattr__("_db", db)
		for entry in Params:
			super().__setattr__(entry, Params[entry])

		if(self.DiscordID):
			super().__setattr__("DiscordID", int(self.DiscordID))

		#get the known permissions
		super().__setattr__("_PermissionIDToName", {})
		super().__setattr__("_PermissionNameToID", {})
		(rows, cur) = self._db._fetchall("Select ID, Name from Permissions", ())
		for entry in rows:
			self._PermissionIDToName[entry["ID"]] = entry["Name"].capitalize()
			self._PermissionNameToID[entry["Name"].capitalize()] = entry["ID"]
			super().__setattr__(entry["Name"].capitalize(), False)
		cur.close()

		if ID or DiscordID:
			if ID:
				#get the name for this role
				(row, cur) = self._db._fetchone("Select DiscordID from Roles where ID=?", (ID,))
				if not row:
					raise Exception("Invalid role ID")
				super().__setattr__("DiscordID", int(row["DiscordID"]))
			else:
				#we were given a name so see if it exists otherwise add it
				(row, cur) = self._db._fetchone("Select ID from Roles where DiscordID=?", (DiscordID,))
				if not row:
					cur.close()
					self._db._execute("Insert into Roles (DiscordID) values (?)", (DiscordID,))

					#now get the ID
					(row, cur) = self._db._fetchone("Select ID from Roles where DiscordID=?", (DiscordID,))
					if not row:
						cur.close()
						raise Exception("Error adding role")

					jdata = dump_to_json({"Type": "AddRole", "DiscordID": DiscordID})
					self._db._logdata(jdata)

				super().__setattr__("ID", row["ID"])

			cur.close()

			(rows, cur) = self._db._fetchall("Select PermissionID from RolePermissions where RoleID=?", (self.ID,))
			for entry in rows:
				super().__setattr__(self._PermissionIDToName[entry["PermissionID"]], True)
			cur.close()

	def __setattr__(self, name, value):
		if name == "ID":
			return
		if name in self._PermissionNameToID:
			value = bool(value)
			super().__setattr__(name, value)
			self._db._UpdateRolePermission(self, self._PermissionNameToID[name], value)
		elif name == "DiscordID":
			super().__setattr__(name, int(value))
			self._db._UpdateRole(self, DiscordID=value)
		else:
			super().__setattr__(name, value)

	def __getitem__(self,name):
			return getattr(self, name)

	def __setitem__(self,name,value):
			setattr(self, name, value)

	def __iter__(self):
		self._iter = list(self._PermissionNameToID.keys())
		return self

	def __next__(self):
		if len(self._iter) == 0:
			raise StopIteration
		return self._iter.pop(0)

class DBConfig:
	def __init__(self, db:Database=None):
		#set defaults
		Params = locals()
		Params.pop("self")
		Params.pop("db")
		super().__setattr__("_db", db)

		#get the known config settings
		super().__setattr__("_ConfigNameToID", {})
		(rows, cur) = self._db._fetchall("Select ID, Name, Value from Config", ())
		for entry in rows:
			self._ConfigNameToID[entry["Name"].capitalize()] = entry["ID"]
			super().__setattr__(entry["Name"].capitalize(), entry["Value"])
		cur.close()

	def __setattr__(self, name, value):
		if name in self._ConfigNameToID:
			super().__setattr__(name, value)
			self._db._UpdateConfig(self._ConfigNameToID[name], name, value)

	def __getattribute__(self, name):
		val = super().__getattribute__(name)
		if name == "_ConfigNameToID":
			return val

		if name in self._ConfigNameToID:
			if (type(val) == str) and val.isnumeric():
				val = int(val)
		return val

	def SetSetting(self, name:str, value):
		name = name.capitalize().replace(" ", "_").replace("-", "_")
		if name not in self._ConfigNameToID:
			self.AddSetting(name, value)
		else:
			setattr(self, name, value)

	def GetSetting(self, name:str):
		name = name.capitalize().replace(" ", "_").replace("-", "_")
		if name not in self._ConfigNameToID:
			return None
		return getattr(self, name)

	def AddSetting(self, name:str, value):
		name = name.capitalize().replace(" ", "_").replace("-", "_")
		if name not in self._ConfigNameToID:
			super().__setattr__(name, value)
			self._ConfigNameToID[name] = self._db._AddConfig(name, value)

	def DeleteSetting(self, name:str):
		name = name.capitalize()
		if name not in self._ConfigNameToID:
			return
		self._db._DeleteConfig(self._ConfigNameToID[name], name)
		super().__delattr__(name)
		self._ConfigNameToID.pop(name)