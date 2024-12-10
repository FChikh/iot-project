from utils import authenticate
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_booked_slots(room=None, start=0, days=30):
    ''' This function retrieves all bookings of specified rooms
        in a given time slot.

        Args:
            room -> List[str]:  list of rooms where we want to 
                                get the booking information, e.g.
                                ["MSA 3.500", "MSA 3.520"].
                                By default is None and selects all rooms
            start -> int:       starting point, in days from now on
            end -> end:         ending point, in days from starting point

        Return:
            filtered_events:    contains a list of dictionnaries which represent 
                                events and contain the most important of each event
    '''


    creds = authenticate.authenticate()

    start = (datetime.now() + timedelta(days=start))
    end = start + timedelta(days=days)
    start = start.isoformat() + "Z"
    end = end.isoformat() + "Z"

    try:
        service = build("calendar", "v3", credentials=creds)

        calendarID_Rooms = "7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"

        event_results = service.events().list(calendarId=calendarID_Rooms, 
                                              timeMin=start, 
                                              timeMax=end,
                                              singleEvents=True,
                                              orderBy="startTime").execute()

        events = event_results.get("items", [])

        if not events:
            print("No upcoming events!")
            return []

        event_res = []

        for event in events:
            start_dt = event["start"].get("dateTime")
            end_dt = event["end"].get("dateTime")

            parsed_start = datetime.fromisoformat(start_dt)
            parsed_end = datetime.fromisoformat(end_dt)

            

            event_res.append({"room": event["location"],
                              "start_time": parsed_start.time(),
                              "end_time": parsed_end.time(),
                              "date": parsed_start.date()})

        if room:
            filtered_events = [event for event in event_res if event.get('room') in room]
        else:
            filtered_events = event_res
        

        '''
        for event in filtered_events:
            print(f'{event["room"]}: {event["start_time"]}-{event["end_time"]} ({event["date"]})')
        '''

        return filtered_events

    except HttpError as error:
        print("An error occured:", error)



get_booked_slots(room=["MSA 3.500"])
