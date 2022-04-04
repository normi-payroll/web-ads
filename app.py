import email
from pprint import pprint
from urllib import response
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, json
from flask_session import Session
from werkzeug.security import generate_password_hash
import datetime

from controller import actions
from controller import middleware as mw
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Landing Page 
@app.route('/', methods=['GET'])
def index():
    #replace with any landing page
    return render_template('Landing/index.html', 
    
    ),200

@app.route('/login', methods=['GET'])
@mw.not_login
def login():
    #replace with any landing page
    return render_template('Landing/log-in.html', 
    whos_loging_in = "Subscriber"
    
    ),200

#ADMIN SECTION
@app.route('/admin')
@app.route('/admin/subscribers')
@mw.admin_required
def subscribers():
    userInfo = None
    if "userInfo" in session:
        userInfo = session["userInfo"]
    subscribers = actions.read_data({ "isAdmin": False }, "subscribers")
    print(subscribers)
    return render_template('subs-list.html',
    userInfo = userInfo,
    subscribers = subscribers,
    link_name = "Subscribers",
    subs = "active",
    ),200

@app.route('/admin/advertisement-list')
@mw.admin_required
def advertisement_list():
    userInfo = None
    if "userInfo" in session:
        userInfo = session["userInfo"]
    advertisement = actions.read_data({}, "schedule")
    return render_template('ads-list.html',
    userInfo = userInfo,
    advertisement = advertisement,
    link_name = "Advertisement List",
    ads_menu="open",
    ads = "active",
    ads_list = "active"
    ),200


@app.route('/content/ads-scheduler')
@app.route('/admin/ads-scheduler')
@mw.login_required
def ads_scheduler():
    userInfo = None
    if "userInfo" in session:
        userInfo = session["userInfo"]
    return render_template("ads-scheduler.html",
    sched="active",
    userInfo = userInfo,
    link_name = "Schedule Ads",
    )

@app.route("/live-ads")
def live_ads():
    now = datetime.datetime.now()
    #get ads schedule today
    data = actions.read_data({ "start": {"$regex" :now.strftime("%Y-%m-%d ")}, "end": {"$regex" :now.strftime("%Y-%m-%d ")} }, "schedule")
    return render_template("live_ads.html",
    ads = data
    )
#END ADMIN SECTION

#API
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        username =  request.form['username']
        password =  request.form['password']

        response = actions.login_process(username, password, session)
        if response['verified']:
            return response, 200
        else:
            return response, 200
    except Exception as e:
        print(e)
        return { "success": False }, 500

@app.route('/api/logout')
def api_logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/api/add_subscriber', methods=["POST"])
def add_subscriber():
    try:
        res = request.json
        data = res["data"]
        data["password"] = generate_password_hash(data["password"])
        if data is not None:
            isNotNone = actions.read_data({ }, "subscribers")
            if isNotNone:
                check = actions.read_data({ "ownerName": data["ownerName"], "email": data["email"], "phone":["phone"] }, "subscribers")
                print(check)
                if len(check) == 0:
                    res = actions.create_data(True, data, "subscribers")
                    if res is not None:
                        return { "msg": "Successfully Created" }, 200
                    else:
                        return { "msg": "Creation Failed" }, 201
                else:
                    return { "msg": "Account already exists!" }, 201
            else:
                res = actions.create_data(True, data, "subscribers")
                if res is not None:
                    return { "msg": "Successfully Created" }, 200
                else:
                    return { "msg": "Creation Failed" }, 201
        else:
            return { "msg": "Creation Failed" }, 201
    except Exception as e:
        print(e)
        return { }, 500

@app.route("/api/send_sms", methods=["POST"])
def send_sms():
    data = request.json
    to = data["to"]
    msg = data["msg"]
    actions.send_sms(to, msg)
    return "ok", 200

@app.route("/api/add_schedule", methods=["POST"])
def add_schedule():
    res = request.json
    print(res["data"])
    added, msg = actions.add_schedule(res['data'])
    print(added, msg)

    return { "ädded": added, "msg": msg}, 200
    

@app.route("/api/get_schedules", methods=["POST"])
def get_schedules():
    try:
        data = actions.read_data({}, "schedule")
        return {"data": data}, 200
    except Exception as e:
        print(e)
        return {"msg": e}, 400

@app.route("/test", methods=["POST"])
def test():
    res = request.json
    data = res["data"]
    print(data)
    to = data["to"]
    msg = data["msg"]
    later = data["later"]
    year = data["year"]
    month =data["month"]
    day = data["day"]
    hour = data["hour"]
    minutes = data["minutes"]
    if later:
        notify_later = actions.create_scheduled_sms(to, msg, year, month, day, hour, minutes, "00")
        print(notify_later)
        return "OK", 200
    else:
        notified = actions.send_sms(to, msg)
        print(notified)
        return "OK", 200
#END API
@app.errorhandler(404)
def not_found(e):
  return redirect(url_for("index"))

if __name__ == "__main__":
	app.run(debug=True, port=5000, host="0.0.0.0")
    #app.run()#for deployment
