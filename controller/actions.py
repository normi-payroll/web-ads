from cmath import e
from venv import create
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash

from datetime import datetime
#import os
from twilio.rest import Client

account_sid = "AC9653bc4a80954b9a4a5f7b7c7e0143a7"
auth_token = "d38bed2ce11328f3e57e4054cc92ab32"
mssid ="MGcb90ca8fa7907b088770bfcaa805e582"
client = Client(account_sid, auth_token)

cloud = "mongodb+srv://user:pass@cluster0.bb3sk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

#cluster = MongoClient("mongodb://localhost:27017/")
cluster = MongoClient(cloud)
db = cluster["LED_ADS"]

#SMS Notification
def create_scheduled_sms(to, msg, year, month, day, hour, minutes, seconds):
	try:
		message = client.messages\
		.create(
			messaging_service_sid=mssid,
			body=msg,
			send_at=datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds)),
			schedule_type='fixed',
			
			to=to
		)
		print(message)
		print(message.sid)
		return True
	except Exception as e:
		print(e)
		return False

def send_sms(to, msg):
	try:
		message = client.messages\
		.create(
			messaging_service_sid=mssid, 
            body=msg,      
            to=to
		)
		print(message)
		print(message.sid)
		return True
	except Exception as e:
		print(e)
		return False 
		
#END SMS Notification

#Dynamic API
def create_data(insertOne, data, table):
	try:
		inserted = None
		if insertOne:
			inserted = db[table].insert_one(data)
		else:
			inserted = db[table].insert_many(data)
		return inserted
	except Exception as e:
		print(e)
		return { "created" : False, "data": None }

def read_data(query, table):
	try:
		res = db[table].find(query)
		print(res)
		if res:
			data = []
			for el in res:
				el["_id"] = str(el["_id"]).replace("ObjectId('","").replace("')","")
				data.append(el)
			return data
		else:
			return None
	except Exception as e:
		print(e)
		return None
		

def update_data(updateOne, upsert, query, data, table):
	data = None
	if updateOne:
		data = db[table].update_one(query, data, upsert)
	else:
		data = db[table].update_many(query, data, upsert)
	return data
#Dynamic API

#Processes
def login_process(username, password, session):
	try:
		user_exists = db.subscribers.find_one({ "$or": [ { "email": username }, { "phone": username } ] }, {'_id': False})
		if len(username) == 0 and len(password) == 0:
			return { "msg": "Please enter your username and password!", "verified": False }
		if user_exists:
			db_password = user_exists['password']
			if check_password_hash(db_password, password):
				del user_exists["password"]
				session["userInfo"] = user_exists
				session["isAdmin"] = user_exists['isAdmin']
				session["isLogin"] = True
				redirect_url = "/"
				if user_exists['isAdmin']:
					redirect_url = "/admin"
				else:
					redirect_url = "/content/ads-scheduler"
				return { "msg": "Successfully Login", "verified": True, "redirect_url": redirect_url }
			else :
				return { "msg": "Please enter your correct password!", "verified": False }
		else:
			return { "msg": "Account is not registered!", "verified": False }
	except Exception as e:
		print(e)
		return { "msg": e, "verified": False }

def add_schedule(data):
	try:
		duplicates = []
		check = None
		if len(data) >1:
			for val in data:
				check = read_data({ "$or": [ { "start": val["start"] }, { "end": val["end"] } ] }, "schedule")
				if check:
					duplicates.append("error")

			if len(duplicates) !=0:
				print(duplicates)
				return False, "Schedule is already taken. Please check the schedule before submitting!"
			else :
				add = create_data(False, data, "schedule")
				if add:
					notified = send_sms_notif(data)
					if notified:
						return True, "Successfully Added"
					else: 
						return True, "Successfully Added"
				else: 
					return False, "Error while adding schedule. Please try again later!"
		else:
			check = read_data({ "$or": [ { "start": data[0]["start"] }, { "end": data[0]["end"] } ] }, "schedule")
			if check:
				print(check)
				return False, "Schedule is already taken. Please check the schedule before submitting!"
			else :
				add = create_data(False, data, "schedule")
				if add:
					notified = send_sms_notif(data)
					if notified:
						return True, "Successfully Added"
					else: 
						return True, "Successfully Added"
				else: 
					return False, "Error while adding schedule. Please try again later!"
	except Exception as e:
		print(e)

def send_sms_notif(data):
	try:
		info = data[0] 
		msg = '''
		Greetings! {} Your video ads already in place for our LED Billboard Advertisement. 

		It will start on {} and will end on {}.
					
		Billing Info:
			Owner Name: {}
			Company: {}
			Package: {}
			Total Days: {}
			Fee per day: {}
			Total Fee: {}
			'''.format(
				info["ownerName"], info["start"], info["end"],
				info["ownerName"], info["company"], info["package"],
				info["totalDays"], info["totalFeePerDay"], info["totalFee"]
			)
		notify = send_sms(info["phoneNumber"], msg )
		if notify:
			#print(msg)	
			end_msg = '''
			Greetings! {} Your video ads is about to expire in our LED Billboard Advertisement.
			Contract Date:
			Every {} from {} up to {}.
			
			Thank You!
			'''.format(info["ownerName"], 
			str(info["start"]).split(" ")[1] +" and "+  str(info["end"]).split(" ")[1],
			str(info["start"]).split(" ")[0],
			str(info["end"]).split(" ")[0],
			)
			end = str(info["end"]).split("-")
			year = end[0]
			month = end[1]
			dayTime = str(end[2]).split(" ")
			day = dayTime[0]
			time = str(dayTime[1]).split(":")
			hour = time[0]
			min = time[1]
			sec = "00"
		
			print(end_msg)
			notify_later = create_scheduled_sms(info["phoneNumber"], end_msg,  year,  month,  day,  hour,  sec,  min)
			if notify_later:
				return True
			else:
				return False
		else:
			return False
	except Exception as e:
		print(e)
#End Processes