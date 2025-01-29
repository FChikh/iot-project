import streamlit as st
from datetime import datetime, timedelta

# Page title
st.title("Room Booking System")

# Create layout containers
with st.container():
    st.header("Booking Details")

    # Select a date
    selected_date = st.date_input("Select a date for your booking:", min_value=datetime.today())

    # Generate 30-minute interval options
    time_intervals = []
    for hour in range(24):
        time_intervals.append(f"{hour:02}:00")
        time_intervals.append(f"{hour:02}:30")

    # Select a timeslot
    st.subheader("Select a time slot")
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.selectbox("Start time:", options=time_intervals)
    with col2:
        end_time = st.selectbox("End time:", options=time_intervals)

    # Validate timeslot
    if time_intervals.index(start_time) >= time_intervals.index(end_time):
        st.warning("End time must be later than start time!")

# Room preferences
with st.container():
    st.header("Room Preferences")
    seating_capacity = st.number_input("Amount of seating facilities needed:", min_value=0, step=1)
    videoprojector_needed = st.checkbox("Is a video projector needed?")
    num_computers = st.number_input("Amount of computers required:", min_value=0, step=1)

    air_quality_preference = st.radio("Air Quality:", options=["Normal", "High"])
    noise_level_preference = st.radio("Noise level:", options=["Normal", "Silent"])

# Submit button
with st.container():
    if st.button("Book Room"):
        # Validate inputs
        if time_intervals.index(start_time) >= time_intervals.index(end_time):
            st.error("Please ensure that your end time is later than your start time.")
        else:
            st.success("Your room booking request has been submitted!")
            st.write(f"**Date:** {selected_date}")
            st.write(f"**Time slot:** {start_time} - {end_time}")
            st.write("**Preferences:**")
            st.write(f"- Seating facilities: {seating_capacity}")
            st.write(f"- Video projector needed: {'Yes' if videoprojector_needed else 'No'}")
            st.write(f"- Computers: {num_computers}")
            st.write(f"- Air quality Preference: {air_quality_preference}")
            st.write(f"- Noise level Preference: {noise_level_preference}")

# Calendar preview
with st.container():
    st.header("Room Availability Calendar")

    # Embed Google Calendar using an iframe
    google_calendar_url = "https://calendar.google.com/calendar/embed?src=7e153f9a22e108db15281a9791412833960a6568cee592790c8bf4ee8b2518de@group.calendar.google.com"
    st.markdown(
        f'<iframe src="{google_calendar_url}" style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>',
        unsafe_allow_html=True,
    )
