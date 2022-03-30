from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from invokes import invoke_http
import requests


#to remove if we dont use rabbit amqp
import direct_amqp_setup
import topic_amqp_setup
import pika
import json



app = Flask(__name__)
CORS(app)


JobsURL = "http://127.0.0.1:5001/jobs"
ApplicationURL = "http://127.0.0.1:5003/applications/"
OwnerNotiURL = "http://127.0.0.1:5010/ownerNotification/"
# check if job is there


#  flow: 
# 1. user send job search information {job search} to job SMS
# 2. 

@app.route("/apply_job", methods=['POST'])
def apply_job():
    try:
        data = request.data.decode("utf-8") #decode bytes --> data received is in bytes; need to decode 
        data = json.loads(data)
        print(data)
        print(JobsURL+"/"+data["JID"])

        # get jobs with the JID
        result = invoke_http(JobsURL+"/"+data["JID"],method ="GET")

        code = result["code"]
        if code not in range (200, 300):

            # send error message to error queue
            message = json.dumps(result["data"])

            topic_amqp_setup.channel.basic_publish(exchange=topic_amqp_setup.exchangename, routing_key="applyjob.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

            # return error
            return jsonify(
                {
                    "code": 500,
                    "data": message,
                }
            ), 500
        else:
            application_result = invoke_http(ApplicationURL+data["JID"],method ="POST",json =data)

            code = application_result['code']


            if code not in range (200, 300):
                # send application failture message to error queue
                message = json.dumps(application_result["data"])
                print(message)

                topic_amqp_setup.channel.basic_publish(exchange=topic_amqp_setup.exchangename, routing_key="applyjob.error", 
                body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
                print('this is my application result', application_result)

                # return error
                return jsonify(
                    {
                        "code": 500,
                        "data": message
                    }
                ), 500
            else:
            #     # notify owner
                notifyOwner(data)

                # send application success message to activity_log queue
                message = json.dumps(application_result["data"])
                print(message)

                topic_amqp_setup.channel.basic_publish(exchange=topic_amqp_setup.exchangename, routing_key="applyjob.info", 
                body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
                print('this is my application result', application_result)
                return jsonify(
                    {
                        "code": 200,
                        "data": json.dumps(application_result)
                    }
                ), 200

    except Exception as e:
        print(e)
        # return "NOT OK"
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while applying for job. " + str(e)
            }
        ), 500

def notifyOwner(data):
    # New: AMQP broker to send message to owner notification
    print('ownernoti ', data)
    message = json.dumps(data)
    direct_amqp_setup.channel.basic_publish(exchange=direct_amqp_setup.exchangename, routing_key="ownerNotification", 
    body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

    # notiresult = invoke_http(OwnerNotiURL+data["CID"],method ="POST",json =data)
    # message = json.dumps(notiresult)
    # if notiresult["code"] not in range(200, 300):

    #     amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="ownerNoti.error", 
    #     body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

    #     # return error
    #     return jsonify(
    #         {
    #             "code": 500,
    #             "data": message
    #         }), 500
    # else:
    #     amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="ownerNoti.info", 
    #     body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

    #     # return error
    #     return jsonify(
    #         {
    #             "code": 200,
    #             "data": message
    #         }), 200


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " applying for a job...")
    app.run(host="0.0.0.0", port=5008, debug=True)


