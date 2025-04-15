#import os
#from twilio.rest import Client
#from django.conf import settings

#def send_sms(mobile_number, message):
   
    # Retrieve Twilio credentials from settings or environment variables
    #account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", os.environ.get("TWILIO_ACCOUNT_SID", ""))
    #auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", os.environ.get("TWILIO_AUTH_TOKEN", ""))
    #twilio_phone_number = getattr(settings, "TWILIO_PHONE_NUMBER", os.environ.get("TWILIO_PHONE_NUMBER", ""))

    # Initialize the Twilio Client
    #client = Client(account_sid, auth_token)

    # Create and send the message using the provided mobile_number parameter
    #sms = client.messages.create(
        #body=message,
        #from_=twilio_phone_number,
        #to=mobile_number  # Ensure mobile_number is a string in E.164 format (e.g., "+60177817784")
    #)

    #return sms.sid

# 