
from __future__ import print_function
from dateutil import parser
import httplib2
import os
import time as s
import signal
import sys
import pytz

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import mraa
import touch_blink as tb

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def signal_handler(signal, frame):
    global statuslight
    statuslight.write(0)
    sys.exit(0)


service = 0 
statuslight = 0 
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    global service
    global statuslight

    signal.signal(signal.SIGINT, signal_handler)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    statuslight = mraa.Gpio(24)
    statuslight.dir(mraa.DIR_OUT)
    statuslight.write(1)

    #go into idle state, wait to get tomorrows events
    idle()
    #tb.alarm()
    #statuslight.write(0)


   

def idle():
    """
Waits until it is time to set alarm. which is 2200 hrs every day. 
    """
    
     #get current time, for the day-year
    timetosetalarm = datetime.datetime.utcnow().isoformat()+ 'Z' # 'Z' indicates UTC time
    #print(timetosetalarm)

    #convert string to datetime, for time comparison purposes
    timetosetalarm = parser.parse(timetosetalarm)

    #set time to grab calendar events at 2200 
    #timetosetalarm = timetosetalarm.utcnow().replace(hour=22, minute=00, second=00,microsecond=00)
    timetosetalarm = timetosetalarm.now().replace(hour=12, minute=00, second=00,microsecond=00)
    timetosetalarm = timetosetalarm.replace(tzinfo=pytz.utc)

    #wait until it is time
    while True:
        #get the current time
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        rightnow = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        rightnow = rightnow.time()

        #for debugging purposes, just calendar events now
        #if rightnow == timetosetalarm:
        if True:
            print('Getting the upcoming 10 events')
            print(timetosetalarm)
            #Google API needs a string for time 
            timetosetalarmstring = timetosetalarm.strftime("%Y-%m-%dT%H:%M:%SZ")
            print(timetosetalarmstring)
            #send request to Google 
            eventsResult = service.events().list(
                calendarId='primary', timeMin=timetosetalarmstring, maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
            events = eventsResult.get('items', [])

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                #start = parser.parse(start).utcnow()
                print(start, event['summary'])

            if not events:
                print('No upcoming events found.')
                continue

            setAlarm(events)
            break
    
                    
            
def setAlarm(events):
    #set count to first event with a time, assume this is zero at start
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])
        #print(start, event['start'].get('dateTime'))
        if event['start'].get('dateTime') != None:
            print('no time for this event')
            eventDateTime = parser.parse(event['start'].get('dateTime'))
            eventDateTime = eventDateTime.astimezone(pytz.UTC)
            eventDateTime = eventDateTime.time().replace(second=0, microsecond=0)
            #print(eventDateTime)
            soundAlarm(eventDateTime)
    #the loop has finished, and none of the events have an applicable start time
    idle()
   
def soundAlarm(alarmTime):
    global statuslight
    while True:
        print(alarmTime)
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        rightnow = datetime.datetime.utcnow().replace(second=0, microsecond=0)
        rightnow = rightnow.time()
        if alarmTime == rightnow:
            statuslight.write(0)
            print('go do it')
            tb.alarm()
            #for debugging purposes, i commented out idle, you would get rid of the break statement in production 
            #idle()
            break
        
        


    
    

if __name__ == '__main__':
    main()
