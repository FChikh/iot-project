from ..authenticate import get_calendar_service

# from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
from datetime import datetime, timedelta
from flask import abort, jsonify
from dateutil import parser



def get_spec_room_bookings(room_id, start_date=None, days=None):

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=days)
        
        service = get_calendar_service()
        calendar_id = os.getenv('GOOGLE_CAL_ID')
        
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z", 
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        bookings = {}
        for event in events:
            room = event["location"]
            temp1 = event["start"].get("dateTime")
            start_time = parser.parse(temp1).strftime('%Y-%m-%d %H:%M:%S')

            
            if room == room_id:
                if room not in bookings:
                    bookings[room] = []
                bookings[room].append(start_time)

        return bookings

    except HttpError as error:
        print(error)
        abort(400, f"Google Calendar API error: {str(error)}")
    except Exception as error:
        print(error)
        abort(500, f"Internal server error: {str(error)}")






def get_all_room_bookings(start_date, days):

    
    try:
        # print(start_date)
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        # print(start_date)
        end_date = start_date + timedelta(days=days)
        # print(end_date)
        
        service = get_calendar_service()
        calendar_id = os.getenv('GOOGLE_CAL_ID')
        
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z", 
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])

        bookings = {}
        for event in events:
            room = event["location"]
            temp1 = event["start"].get("dateTime")
            start_time = parser.parse(temp1).strftime('%Y-%m-%d %H:%M:%S')
            print(start_time)

            
            if room not in bookings:
                bookings[room] = []
            bookings[room].append(start_time)

        return bookings

    except HttpError as error:
        print(error)
        abort(400, f"Google Calendar API error: {str(error)}")
    except Exception as error:
        print(error)
        abort(500, f"Internal server error: {str(error)}")



