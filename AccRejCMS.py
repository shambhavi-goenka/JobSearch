from flask import Flask, request, jsonify
import json
import pyrebase as pb
from invokes import invoke_http
from flask_cors import CORS,cross_origin
app = Flask(__name__)
CORS(app)

# app.config['CORS_HEADERS'] = 'Content-Type'

ApplicationSMS = "http://127.0.0.1:5003/applications"
OwnerStatusSMS = "http://127.0.0.1:5004/status/"



@app.route("/get_applications/<string:CID>") # process you auto fill company ID
def owner_get_applications(CID):
    try:
        applications = invoke_http(ApplicationSMS+"/company/"+CID,method = "GET")
        return applications
    except Exception as e:
        return "NOT OK"



@app.route("/process_application/<string:AID>",methods = ["PUT"]) # process you auto fill company ID
def owner_process_application(AID):
    try:
        data = request.data.decode("utf-8") #decode bytes --> data received is in bytes; need to decode 
        data = json.loads(data) #gets
        print(data)
        applications = invoke_http(OwnerStatusSMS+AID,method = "PUT",json = data)
        return jsonify(applications)
    except Exception as e:
        print(e)

        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the job. " + str(e)
            }
        ), 500

def send_to_broker(): #for the broker
    pass

if __name__ == "__main__":
    app.run(port = 5006,debug = True)