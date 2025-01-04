import connexion
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
import os
import pytz
import traceback

from ..authenticate import get_calendar_service
from ..helper_funcs import translate_room_id



def post_book_room_id(body, room_id):
    """Book a specific room"""
    print("Starting booking process...")  # Debug log
    print(f"Received body: {body}")      # Debug log
    print(f"Room ID: {room_id}")         # Debug log
    
    try:
        # Extract required fields from body
        responsible = body.responsible
        description = body.description
        start_timestamp = body.start_timestamp
        
        print(f"Extracted fields: responsible={responsible}, description={description}, start_timestamp={start_timestamp}")  # Debug log
        
        # Parse the start timestamp
        if isinstance(start_timestamp, str):
            start_time = datetime.strptime(start_timestamp, '%Y-%m-%d %H:%M:%S')
        else:
            start_time = start_timestamp

        # Convert to Europe/Luxembourg timezone (GMT+01:00 or GMT+02:00 depending on daylight saving time)
        timezone = pytz.timezone('Europe/Luxembourg')  # Use the appropriate timezone
        start_time = timezone.localize(start_time)  # Localize the time to Europe/Luxembourg timezone
        end_time = start_time + timedelta(minutes=30)

        print(f"Parsed timestamps: start={start_time}, end={end_time}")  # Debug log
        
        # Check for existing bookings
        service = get_calendar_service()
        calendar_id = os.getenv('GOOGLE_CAL_ID')
        
        print(f"Calendar ID: {calendar_id}")  # Debug log
        
        if not calendar_id:
            raise ValueError("GOOGLE_CAL_ID environment variable is not set")

        # Check for overlapping events
        events = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat(),  # Send in Europe/Luxembourg time zone
            timeMax=end_time.isoformat(),    # Same for end time
            singleEvents=True
        ).execute().get("items", [])
        
        print("Arrived 3")

        # Check if room is already booked
        for event in events:
            if event.get("location") == room_id:
                return {
                    "status": "error",
                    "message": "Room is already booked for the specified time slot."
                }, 409
        print("Arrived 4")

        
        # Create the calendar event
        event = {
            'summary': f'Room {translate_room_id(room_id)}',
            'location': room_id,
            'description': f'{body.description} ({responsible})',
            'start': {
                'dateTime': start_time.isoformat(),  # Send the time in ISO format without "Z"
                'timeZone': 'Europe/Luxembourg',     # Set the timezone explicitly
            },
            'end': {
                'dateTime': end_time.isoformat(),    # Same for the end time
                'timeZone': 'Europe/Luxembourg',
            },
        }
        print("Arrived 5")
        
        service.events().insert(calendarId=calendar_id, body=event).execute()
        print("Arrived 6")
        
        return {
            "status": "success",
            "message": "Room booked successfully."
        }, 200

    except ValueError as error:
        print(f"ValueError occurred: {error}")
        print(f"ValueError traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Invalid request data: {str(error)}"
        }, 400
    except HttpError as error:
        print(f"Google Calendar API error occurred: {error}")
        print(f"HttpError traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Google Calendar API error: {str(error)}"
        }, 400
    except Exception as error:
        print(f"Unexpected error occurred: {error}")
        print(f"Error type: {type(error)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Internal server error: {str(error)}"
        }, 500

