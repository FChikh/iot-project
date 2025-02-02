import streamlit as st
from datetime import datetime, timedelta
import requests
import time
import json

def fetch_api_data(url: str, retries: int = 5, backoff_factor: float = 1.0):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.write(f"API request failed (attempt {attempt+1}/{retries}): {str(e)}")
            if attempt == retries - 1:
                return None
            sleep_time = backoff_factor * (2 ** attempt)
            time.sleep(sleep_time)
        except json.JSONDecodeError as e:
            st.write(f"Failed to parse JSON response: {str(e)}")
            return None
    return None

def fetch_room_ranking(date, start_time, end_time, seating_capacity, computer_class, pc, projector, 
                         blackboard, smartboard, whiteboard, microphone, air_quality_preference, 
                         noise_level_preference, lighting_preference):
    api_url = (
        f"http://booking_system:8081/rank-rooms?date={date}"
        f"&start_time={start_time}&end_time={end_time}"
        f"&seating_capacity={seating_capacity}&projector={projector}"
        f"&blackboard={blackboard}&smartboard={smartboard}"
        f"&microphone={microphone}&computer_class={computer_class}"
        f"&pc={pc}&whiteboard={whiteboard}"
        f"&air_quality_preference={air_quality_preference.lower()}"
        f"&noise_level={noise_level_preference.lower()}"
        f"&lighting={lighting_preference.lower()}"
    )
    return fetch_api_data(api_url)

def send_booking(room_id, date, start_time, end_time, user_name, description):
    api_url = "http://booking_system:8081/bookings"
    body = {
        "room_id": room_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "user_name": user_name,
        "description": description,
    }
    try:
        response = requests.post(api_url, json=body)
        response.raise_for_status()
        return True
    except Exception as e:
        return False

# --------------------
# Session State Initialization
# --------------------
if "availability_data" not in st.session_state:
    st.session_state.availability_data = None
if "current_search" not in st.session_state:
    st.session_state.current_search = None
if "message" not in st.session_state:
    st.session_state.message = None  # This will hold success or error messages

# --------------------
# Booking Details Input
# --------------------
st.title("Room Booking System")

with st.container():
    st.header("Booking Details")
    # User details for booking (do not affect search parameters)
    user_name = st.text_input("Enter your name for booking:")
    course_name = st.text_input("Enter course name:")

    date = st.date_input("Select a date for your booking:", min_value=datetime.today())
    
    # Generate time intervals from 07:00:00 to 23:30:00
    time_intervals = []
    for hour in range(7, 24):
        time_intervals.append(f"{hour:02}:00:00")
        time_intervals.append(f"{hour:02}:30:00")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.selectbox("Start time:", options=time_intervals)
    with col2:
        end_time = st.selectbox("End time:", options=time_intervals)

# --------------------
# Room Preferences Input
# --------------------
with st.container():
    st.header("Room Preferences")
    seating_capacity = st.number_input("Required seating capacity:", min_value=10, step=1)
    col3, col4 = st.columns(2)
    with col3:
        projector = st.checkbox("Projector")
        computer_class = st.checkbox("Computer Class")
        pc = st.checkbox("Teacher PC")
        air_quality_preference = st.radio("Air Quality:", options=["Normal", "High"])
        noise_level_preference = st.radio("Noise level:", options=["Normal", "Silent"])
    with col4:
        blackboard = st.checkbox("Blackboard")
        whiteboard = st.checkbox("Whiteboard")
        smartboard = st.checkbox("Smartboard")
        microphone = st.checkbox("Microphone")
        lighting_preference = st.radio("Lighting:", options=["Normal", "Bright"])

# --------------------
# Clear Ranking When Search Parameters Change
# --------------------
# Build a tuple from the search parameters (excluding user_name and course_name)
new_search_key = (
    str(date), start_time, end_time, seating_capacity,
    projector, computer_class, pc, blackboard, smartboard,
    whiteboard, microphone, air_quality_preference,
    noise_level_preference, lighting_preference
)

if st.session_state.current_search is None:
    st.session_state.current_search = new_search_key
elif st.session_state.current_search != new_search_key:
    st.session_state.current_search = new_search_key
    st.session_state.availability_data = None
    st.session_state.message = None

# --------------------
# Check Availability and Message Container
# --------------------
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
                computer_class=computer_class,
                pc=pc,
                projector=projector,
                blackboard=blackboard,
                smartboard=smartboard,
                whiteboard=whiteboard,
                microphone=microphone,
                air_quality_preference=air_quality_preference,
                noise_level_preference=noise_level_preference,
                lighting_preference=lighting_preference
            )
        st.session_state.availability_data = data  # Save the fetched ranking data
        st.session_state.message = None  # Clear any previous message

# Message container (will display booking confirmation or error) immediately below Check Availability
message_placeholder = st.empty()
if st.session_state.message:
    # Display the message in a colored box (using st.success or st.error)
    if st.session_state.message.get("type") == "success":
        message_placeholder.success(st.session_state.message.get("text"))
    else:
        message_placeholder.error(st.session_state.message.get("text"))

# --------------------
# Booking Callback Function
# --------------------
def book_room(room, user_name, course_name, date, start_time, end_time):
    # Attempt to book the room and update the session state accordingly.
    if send_booking(room['room_id'], date, start_time, end_time, user_name, course_name):
        st.session_state.availability_data = None  # Clear the ranking list
        st.session_state.message = {"type": "success", "text": f"Successfully booked {room['room_id']}!"}
    else:
        st.session_state.message = {"type": "error", "text": f"An error occured while booking {room['room_id']}, try again later"}

# --------------------
# Display Room Ranking if Available
# --------------------
if st.session_state.availability_data is not None:
    data = st.session_state.availability_data
    if data:
        st.success(f"Found {len(data)} available rooms!")
        for room in data:
            with st.expander(f"Rank #{room['rank']} - {room['room_id']} (Score: {room['score']:.2f})", expanded=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"**Capacity:** {room['capacity']} seats")
                    
                    st.markdown("**Features:**")
                    feature_cols = st.columns(2)
                    features = [
                        ("Projector", room['projector']),
                        ("Computer Class", room['computer-class']),
                        ("Teacher PC", room['pc']),
                        ("Blackboard", room['blackboard']),
                        ("Whiteboard", room['whiteboard']),
                        ("Smartboard", room['smartboard']),
                        ("Microphone", room['microphone'])
                    ]
                    
                    with feature_cols[0]:
                        for feature, value in features[:4]:
                            st.write(f"{'✅' if value else '❌'} {feature}")
                    
                    with feature_cols[1]:
                        for feature, value in features[4:]:
                            st.write(f"{'✅' if value else '❌'} {feature}")
                    
                    st.markdown("**Environmental Conditions:**")
                    env_cols = st.columns(2)
                    with env_cols[0]:
                        st.metric("Temperature", f"{room['temperature']:.1f}°C")
                        st.metric("CO₂", f"{room['co2']:.1f} ppm")
                    with env_cols[1]:
                        st.metric("Noise Level", f"{room['noise']:.1f} dB")
                        st.metric("Lighting", f"{room['light']:.1f} lux")
                
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

# --------------------
# Calendar Preview
# --------------------
with st.container():
    st.header("Room Availability Calendar")
    google_calendar_url = "https://calendar.google.com/calendar/embed?src=7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"
    st.markdown(
        f'<iframe src="{google_calendar_url}" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>',
        unsafe_allow_html=True,
    )
