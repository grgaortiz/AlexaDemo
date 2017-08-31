import urllib2
import json

API_BASE="https://dev.datariver.me/api"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.echo-sdk-ams.app.bd304b90-xxxx-xxxx-xxxx-xxxxd4772bab"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetStatus":
        return get_system_status()
    elif intent_name == "GetElevators":
        return get_elevator_status()
    elif intent_name == "GetTrainTimes":
        return get_train_times(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "nThrive Analytics - Thanks"
    speech_output = "Thank you for using the nThrive Analytics skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "nThrive Analytics"
    speech_output = "Welcome to the Alexa nThrive Analytics skill. " \
                    "You can ask me for platform stats such as users."
    reprompt_text = "Please ask me for platform stats, " \
                    "for example Users."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_total_users(intent):
    session_attributes = {}
    card_title = "nThrive Analytics Users"
    speech_output = "I'm not sure which platform stat you're looking for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which platform stat you're looking for. " \
                    "Try asking about Users for example."
    should_end_session = False

    if "Metric" in intent["slots"]:
        metric_name = intent["slots"]["Station"]["value"]
        card_title = "nThrive Analytics " + metric_name.title()
        response = urllib2.urlopen(API_BASE + "/platform/index.php")
        stats = json.load(response)   
        speech_output = "nThrive Analytics " + metric_name + " is " + stats["total"] + "."
        reprompt_text = ""
            

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
