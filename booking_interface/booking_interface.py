import streamlit as st
from datetime import datetime, timedelta
import requests
import time
import json


def fetch_api_data(url: str, retries: int = 5, backoff_factor: float = 1.0):
    """
    Fetch JSON data from the provided API URL with retry logic.

    :param url: The API endpoint URL.
    :param retries: Maximum number of retry attempts.
    :param backoff_factor: Factor used to compute sleep time between retries.
    :return: Parsed JSON data if successful, otherwise None.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.write(f"API request failed (attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt == retries - 1:
                return None
            sleep_time = backoff_factor * (2 ** attempt)
            time.sleep(sleep_time)
        except json.JSONDecodeError as e:
            st.write(f"Failed to parse JSON response: {str(e)}")
            return None
    return None


def fetch_room_ranking(date: str, start_time: str, end_time: str, seating_capacity: int, 
                    pc: bool, projector: bool, blackboard: bool, 
                       smartboard: bool, whiteboard: bool, microphone: bool, 
                       temperature_preference: str, air_quality_preference: str, 
                       noise_level_preference: str, lighting_preference: str,
                       equipment_weight: int, temperature_weight: int,
                       air_quality_weight: int, noise_weight: int,
                       lighting_weight: int):
    """
    Build the API URL with query parameters and fetch the ranked list of available rooms.
    
    :return: JSON response with room ranking data.
    """
    api_url = (
        f"http://booking_system:8081/rank-rooms?date={date}"
        f"&start_time={start_time}&end_time={end_time}"
        f"&seating_capacity={seating_capacity}&projector={projector}"
        f"&blackboard={blackboard}&smartboard={smartboard}"
        f"&microphone={microphone}"
        f"&pc={pc}&whiteboard={whiteboard}"
        f"&air_quality_preference={air_quality_preference.lower()}"
        f"&noise_level={noise_level_preference.lower()}"
        f"&lighting={lighting_preference.lower()}"
        f"&temperature={temperature_preference.lower()}"
        f"&equipment_weight={equipment_weight}"
        f"&temperature_weight={temperature_weight}"
        f"&air_quality_weight={air_quality_weight}"
        f"&noise_weight={noise_weight}"
        f"&light_weight={lighting_weight}"
    )
    return fetch_api_data(api_url)


def send_booking(room_id: str, date: str, start_time: str, end_time: str, user_name: str, description: str) -> bool:
    """
    Sends booking requests for each half-hour timeslot to the room service.

    :param room_id: The identifier of the room to book.
    :param date: The booking date in 'YYYY-MM-DD' format.
    :param start_time: Start time in 'HH:MM:SS' format.
    :param end_time: End time in 'HH:MM:SS' format.
    :param user_name: Name of the user making the booking.
    :param description: Booking description (e.g., course name).
    :return: True if all bookings succeed; otherwise, False.
    """
    api_url = f"http://restapi_rooms:8080/book/rooms/{room_id}"

    # Convert string timestamps to datetime objects.
    start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")

    # Generate a list of half-hour timeslots.
    timeslots = []
    current_slot = start_dt
    while current_slot < end_dt:
        timeslots.append(current_slot)
        current_slot += timedelta(minutes=30)

    all_successful = True
    errors = []

    # Send a booking request for each half-hour timeslot.
    for slot in timeslots:
        slot_str = slot.strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "start_timestamp": slot_str,
            "responsible": user_name,
            "description": description
        }
        try:
            response = requests.post(api_url, json=payload)
            if not response.ok:
                all_successful = False
                errors.append({
                    "timeslot": slot_str,
                    "status_code": response.status_code,
                    "response": response.text
                })
        except Exception as e:
            all_successful = False
            errors.append({
                "timeslot": slot_str,
                "error": str(e)
            })

    if not all_successful:
        print("Some booking requests failed:", errors)
    return all_successful


def generate_time_intervals(start_hour: int = 7, end_hour: int = 23) -> list:
    """
    Generate time intervals from start_hour to end_hour in half-hour increments.

    :return: List of time strings in 'HH:MM:SS' format.
    """
    intervals = []
    for hour in range(start_hour, end_hour + 1):
        intervals.append(f"{hour:02}:00:00")
        if end_hour != 24:
            intervals.append(f"{hour:02}:30:00")
    return intervals


def book_room(room: dict, user_name: str, course_name: str, date: str, start_time: str, end_time: str):
    """
    Attempt to book the selected room and update session state accordingly.
    
    :param room: Room data as a dictionary.
    """
    if send_booking(room['room_id'], date, start_time, end_time, user_name, course_name):
        st.session_state.availability_data = None  # Clear available rooms list after successful booking.
        st.session_state.message = {
            "type": "success", 
            "text": f"Successfully booked {room['room_id']}!"
        }
    else:
        st.session_state.message = {
            "type": "error", 
            "text": f"An error occurred while booking {room['room_id']}. Please try again later."
        }


# Initialize session state variables.
if "availability_data" not in st.session_state:
    st.session_state.availability_data = None
if "current_search" not in st.session_state:
    st.session_state.current_search = None
if "message" not in st.session_state:
    st.session_state.message = None  # Holds success or error messages.

# Page Title
st.title("Room Booking System")

##############################
# Booking Details Container  #
##############################
with st.container():
    st.header("Booking Details")
    # User details for booking (these do not affect search parameters).
    user_name = st.text_input("Enter your name for booking:")
    course_name = st.text_input("Enter course name:")

    date = st.date_input("Select a date for your booking:", min_value=datetime.today())

    # Generate time intervals from 07:00:00 to 23:30:00.
    time_intervals = generate_time_intervals(start_hour=7, end_hour=19)

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.selectbox("Start time:", options=time_intervals)
    with col2:
        end_time = st.selectbox("End time:", options=time_intervals)


##############################
# Room Preferences Container #
##############################
with st.container():
    st.header("Room Preferences")
    seating_capacity = st.number_input("Required seating capacity:", min_value=10, step=1)
    
    col3, col4 = st.columns(2)
    with col3:
        projector = st.checkbox("Projector")
        pc = st.checkbox("Computer Classroom")
        microphone = st.checkbox("Microphone")
    with col4:
        blackboard = st.checkbox("Blackboard")
        whiteboard = st.checkbox("Whiteboard")
        smartboard = st.checkbox("Smartboard")
    
    col5, col6 = st.columns(2)
    with col5:
        temperature_preference = st.radio("Temperature:", options=["Cool", "Moderate", "Warm"])
        air_quality_preference = st.radio("Air Quality:", options=["Normal", "High"])
    with col6:
        noise_level_preference = st.radio("Noise level:", options=["Normal", "Silent"])
        lighting_preference = st.radio("Lighting:", options=["Normal", "Bright"])
    
    st.subheader("Preference Weights (1-9)")
    col7, col8, col9, col10, col11 = st.columns(5)
    with col7:
        equipment_weight = st.slider("Equipment", 1, 9, 1)
    with col8:
        temperature_weight = st.slider("Temperature", 1, 9, 1)
    with col9:
        air_quality_weight = st.slider("Air Quality", 1, 9, 1)
    with col10:
        noise_weight = st.slider("Noise", 1, 9, 1)
    with col11:
        lighting_weight = st.slider("Lighting", 1, 9, 1)


##############################
# Handle Search State        #
##############################
# Build a tuple from the search parameters (excluding user_name and course_name).
new_search_key = (
    str(date), start_time, end_time, seating_capacity,
    projector, pc, blackboard, smartboard,
    whiteboard, microphone, temperature_preference,
    air_quality_preference, noise_level_preference, lighting_preference,
    equipment_weight, temperature_weight, air_quality_weight, noise_weight, lighting_weight
)

# Update search state if search parameters change.
if st.session_state.current_search is None:
    st.session_state.current_search = new_search_key
elif st.session_state.current_search != new_search_key:
    st.session_state.current_search = new_search_key
    st.session_state.availability_data = None
    st.session_state.message = None


##############################
# Check Availability Button  #
##############################
if st.button("Check Availability"):
    if time_intervals.index(start_time) >= time_intervals.index(end_time):
        st.error("End time must be later than start time!")
    else:
        with st.spinner("Searching for available rooms..."):
            data = fetch_room_ranking(
                date=str(date),
                start_time=start_time,
                end_time=end_time,
                seating_capacity=seating_capacity,
                pc=pc,
                projector=projector,
                blackboard=blackboard,
                smartboard=smartboard,
                whiteboard=whiteboard,
                microphone=microphone,
                temperature_preference=temperature_preference,
                air_quality_preference=air_quality_preference,
                noise_level_preference=noise_level_preference,
                lighting_preference=lighting_preference,
                equipment_weight=equipment_weight,
                temperature_weight=temperature_weight,
                air_quality_weight=air_quality_weight,
                noise_weight=noise_weight,
                lighting_weight=lighting_weight
            )
        st.session_state.availability_data = data  # Save the fetched ranking data.
        st.session_state.message = None  # Clear any previous messages.

##############################
# Message Display Container  #
##############################
message_placeholder = st.empty()
if st.session_state.message:
    message_type = st.session_state.message.get("type")
    message_text = st.session_state.message.get("text")
    if message_type == "success":
        message_placeholder.success(message_text)
    else:
        message_placeholder.error(message_text)


##############################
# Display Available Rooms    #
##############################
if st.session_state.availability_data is not None:
    available_rooms = st.session_state.availability_data
    if available_rooms:
        st.success(f"Found {len(available_rooms)} available rooms!")
        for room in available_rooms:
            with st.expander(f"Rank #{room['rank']} - {room['room_id']} (Score: {room['score']:.2f})", expanded=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**Capacity:** {room['capacity']} seats")

                    # Display room features.
                    st.markdown("**Features:**")
                    feature_cols = st.columns(2)
                    features = [
                        ("Projector", room['projector']),
                        ("Computer Classroom", room['pc']),
                        ("Blackboard", room['blackboard']),
                        ("Whiteboard", room['whiteboard']),
                        ("Smartboard", room['smartboard']),
                        ("Microphone", room['microphone'])
                    ]
                    with feature_cols[0]:
                        for feature, value in features[:3]:
                            st.write(f"{'✅' if value else '❌'} {feature}")
                    with feature_cols[1]:
                        for feature, value in features[3:5]:
                            st.write(f"{'✅' if value else '❌'} {feature}")


                    # Display environmental conditions.
                    st.markdown("**Environmental Conditions:**")
                    brightness = "Bright" if room['light'] >= 900 else "Normal"
                    if room['co2'] < 600 and room['pm2_5'] < 5 and room['pm10'] < 10 and room['voc'] < 100:
                        air_quality = "High"
                    else:
                        air_quality = "Normal"

                    env_cols = st.columns(3)
                    with env_cols[0]:
                        st.metric("Temperature", f"{room['temperature']:.1f}°C")
                        st.metric("Air Quality", air_quality)
                    with env_cols[1]:
                        st.metric("Noise Level", f"{room['noise']:.1f} dB")
                        st.metric("Lighting", brightness)
                    with env_cols[2]:
                        st.metric("Humidity", f"{room['humidity']:.1f} %")

                with cols[1]:
                    if user_name and course_name:
                        st.button(
                            f"Book {room['room_id']}",
                            key=f"book_{room['room_id']}",
                            on_click=book_room,
                            args=(room, user_name, course_name, str(date), start_time, end_time)
                        )
                    else:
                        st.warning("Enter your name and course name above to book")
    else:
        st.warning("No available rooms found matching your criteria")


##############################
# Room Availability Calendar #
##############################
with st.container():
    st.header("Room Availability Calendar")
    google_calendar_url = (
        "https://calendar.google.com/calendar/embed?"
        "src=7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"
    )
    st.markdown(
        f'<iframe src="{google_calendar_url}" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>',
        unsafe_allow_html=True,
    )