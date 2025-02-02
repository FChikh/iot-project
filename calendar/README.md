# Google Calendar Integration for Room Booking

The Google Calendar integration serves as the backbone
for managing room bookings in our IoT project. 
By leveraging Google’s infrastructure, the REST API gains the ability 
to retrieve existing bookings and create new reservations programmatically, 
ensuring reliability and synchronization across users. 
In the following you can find an overview of the implementation, design choices, and challenges addressed.

## Design Choices & Key Features
### Predefined Booking Attributes
To ensure consistency, bookings require three attributes in the POST request:
- `responsible`: Identifies the person or entity making the booking.
- `description`: Provides context (e.g., "Math 101 Lecture").
- `start\_timestamp`: Defines the booking start time in `YYYY-MM-DD HH:MM:SS` format.
This structure simplifies validation and aligns with Google Calendar’s event model.

### 30-Minute Time Slots
Bookings are restricted to fixed 30-minute intervals, 
mirroring the design of our university’s existing room-booking system (e.g., Affluences). 
Benefits include:
- Simplified conflict detection: Slots are checked at 30-minute increments (e.g., 14:00–14:30, 14:30–15:00).
- Reduced complexity: Avoids the need for dynamic slot calculation algorithms.
- User familiarity: Matches the workflow users already expect.

### Headless Authentication with a Service Account
A dedicated Google Cloud service account was configured to enable secure, browserless authentication. 
Key steps included:
- Generating OAuth2 credentials (JSON key file) for machine-to-machine communication.
- Assigning calendar permissions to the service account.
- Using the `google-auth` and `google-api-python-client` libraries to handle token refresh and API calls.
This setup allows the Raspberry Pi (running headlessly) to interact with Google Calendar without manual login.

### Conflict Detection & Validation
Before creating a booking, the API:
- Checks the calendar for existing events in the requested 30-minute slot using Google’s freebusy query.
- Returns a 409 Conflict error if the slot is occupied.
- Validates timestamp formatting to prevent malformed requests.

## Key Challenges
### Service Account Configuration
Google’s documentation offers multiple authentication methods (OAuth2, API keys, service accounts), 
but configuring a service account for headless machine-to-machine access required careful navigation. 
Challenges included:
- Understanding IAM roles to grant minimum necessary permissions (e.g., Calendar API Editor).
- Debugging token refresh issues in a headless environment.

### Time Slot Management
Deciding how to represent and validate bookings involved trade-offs:
- Fixed vs. Flexible Slots: While 30-minute slots simplified implementation, they required being precise on edge cases
- Time Zone Handling: Ensuring timestamps were converted to the calendar’s local time zone (e.g., UTC+1) to avoid mismatches.



