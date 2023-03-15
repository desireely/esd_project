from flask import Flask, jsonify, request
from utils import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import amqp_setup
from dotenv.main import load_dotenv

load_dotenv()

app = Flask(__name__)


# TO DO

# listing created
# after bidding successful
# when someone overbid you
# when the auction is about to end
# when the auction end
# inform the seller and final highest bidder that bid is successful and they have 7 days to complete transaction
# reminder on the 6th day if transaction not completed
# transaction completed
# seller notified to resell or delete listing when fail

@app.route('/notify_new_listing', methods=['POST'])

def notify_new_listing():
    # seller_data = request.get_json()

    seller_data = {
        "username" : "gay_seller",
        "listing_name" : "ball",
        "listing_description" : "stripes",
        "starting_bid" : 3000,
        "datetime_created" : 1647213165,
        "auction_end": 1647213166,
    }
    
    # check if data needed is available 
    if seller_data and check_attributes(seller_data, ["username", "listing_name", "listing_description", "starting_bid", "datetime_created", "auction_end"]):
        message = Mail(
            from_email='bidbuddy2023@gmail.com',
            to_emails='oreoanytime@gmail.com',
            subject='Listing Posted Successfully!',
            html_content='<strong>Hello, this is a test email.</strong>')
        
        # to edit: html content (email content)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)

        # print(response.status_code, response.body)
        # print(response)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="newlist", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        
        return jsonify(
            {
                "code": 201,
                "message": "good"
            }
        ), 201
    
    return jsonify(
        {
            "code": 400,
            "message": "bad"
        }
    ), 400

    # return if no data or missing data 

def send_email_consumer(channel, method, properties, body):
    message = Mail.from_json(body)
    try:
        response = sg.send(message)
        print(f"Email sent to {message.to[0].email} with status code {response.status_code}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error sending email to {message.to[0].email}: {e}")
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)


@app.route('/notify_bidsuccess', methods=['POST'])
def notify_bidsuccess() :
    # seller_data = request.get_json()

    bid_data = {
        "username" : "lesbuyer",
        "listing_name" : "ball",
        "listing_description" : "stripes",
        "bid_price" : 3100,
        "bid_datetime" : 1647213165,
        "auction_end": 1647213166,
        "bid_count" : 1,
    }
    #bid count to count number of bidder
    
    # check if data needed is available 
    if bid_data and check_attributes(bid_data, ["username", "listing_name", "listing_description", "bid_price", "bid_datetime", "auction_end", "bid_count"]): 
        message = Mail(
            from_email='bidbuddy2023@gmail.com',
            to_emails='oreoanytime@gmail.com',
            subject='Bid Successful',
            html_content='<strong>Hi, you are the current highest bidder.</strong>')
        
        # to edit: html content (email content)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)

        # print(response.status_code, response.body)
        # print(response)

        return jsonify(
            {
                "code": 200,
                "data": bid_data['username']
            }
        )
    
    return jsonify(
        {
            "code": 400,
            "message": "bad"
        }
    ), 400


@app.route('/notify_overbid', methods=['POST'])
def notify_overbid() :
    # seller_data = request.get_json()

    bid_data = {
        "username" : "lesbuyer",
        "listing_name" : "ball",
        "listing_description" : "stripes",
        "bid_price" : 3100,
        "new_highest_bid" : 3200,
        "bid_datetime" : 1647213165,
        "auction_end": 1647213166,
        "bid_count" : 2,
    }
    
    #bid count to count number of bidder

    # check if data needed is available 
    if bid_data and check_attributes(bid_data, ["username", "listing_name", "listing_description", "bid_price", "bid_datetime", "auction_end", "bid_count"]):
        message = Mail(
            from_email='bidbuddy2023@gmail.com',
            to_emails='oreoanytime@gmail.com',
            subject='Overbidded',
            html_content='<strong>Hi, you have been overbidded.</strong>')
        
        # to edit: html content (email content)

        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)

        # print(response.status_code, response.body)
        # print(response)

        return jsonify(
            {
                "code": 200,
                "data": bid_data['username']
            }
        )
    
    return jsonify(
        {
            "code": 400,
            "message": "bad"
        }
    ), 400



if __name__ == '__main__':
    app.run(port=5000, debug=True)
