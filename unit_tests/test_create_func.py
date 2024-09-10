def open_discord():
    import subprocess
    subprocess.call(['open', '-a', 'Discord'])

def reposition_discord():
    import subprocess
    
    # Get the current screen size
    screen_size = subprocess.run(["osascript", "-e", "tell application \"System Events\" to get {width, height} of bounding rectangle of desktop"], capture_output=True, text=True)
    width, height = map(int, screen_size.stdout.split(","))
    
    # Calculate the new position and size for the Discord application
    new_width = width // 2
    new_height = height
    new_x = 0
    new_y = 0
    
    # Reposition the Discord window using AppleScript
    script = f'''
    tell application "Discord"
        activate
        set the bounds of the front window to {{{new_x}, {new_y}, {new_x + new_width}, {new_y + new_height}}}
    end tell
    '''
    subprocess.run(["osascript", "-e", script])



def send_text(phone_number, message):
    import requests
    
    url = "https://api.textservice.com/send"  # Example URL, replace with actual service
    payload = {
        'to': phone_number,
        'message': message
    }
    response = requests.post(url, json=payload)
    return response.status_code, response.json()

def send_text_message(phone_number, message):
    import smtplib
    from email.mime.text import MIMEText

    # Example: using a generic SMS gateway
    # This will vary depending on the carrier
    sms_gateway = f"{phone_number}@txt.att.net"  # example for AT&T
    
    msg = MIMEText(message)
    msg['Subject'] = 'Text Message'
    msg['From'] = 'your_email@example.com'
    msg['To'] = sms_gateway

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        server.send_message(msg)

# send_text_message("+16692248461", "Hello, this is a test message")

def open_netflix_in_safari():
    import subprocess
    subprocess.run(["open", "-a", "Safari", "https://www.netflix.com"])

# open_netflix_in_safari()

def check_emails_in_arc():
    import subprocess
    
    try:
        # Command to open Arc browser
        subprocess.run(["open", "-a", "Arc", "https://mail.google.com"], check=True)
        return "Arc browser opened with Gmail."
    except Exception as e:
        return f"An error occurred: {e}"
def add_meeting(calendar, meeting_details): 
    calendar.append(meeting_details) 
    return calendar

def add_meeting_to_calendar(meeting_title, meeting_date, meeting_time, meeting_duration, attendees, location, notes):
    import datetime
    import applescript

    start_time = datetime.datetime.strptime(f"{meeting_date} {meeting_time}", '%Y-%m-%d %H:%M')
    end_time = start_time + datetime.timedelta(hours=meeting_duration)

    script = f'''
    tell application "Calendar"
        set new_event to make new event at end of events of calendar "Calendar" with properties {{
            summary:"{meeting_title}",
            start date:date "{start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            end date:date "{end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            location:"{location}",
            description:"{notes}"
        }}
        repeat with attendee in {attendees}
            make new attendee at end of attendees of new_event with properties {{email:attendee}}
        end repeat
    end tell
    '''
    
    applescript.run(script)
    print("Meeting added to calendar")
# add_meeting_to_calendar("Team Meeting", "2024-9-11", "09:00", 1, ["adit.kadepurkar@gmail.com"], "Office", "Discuss project progress")

def add_event_to_calendar(title, start_time, end_time, location=None, notes=None):
    import subprocess
    from datetime import datetime
    
    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S").strftime("%m/%d/%Y %H:%M:%S")

    # Start building the AppleScript
    script = f'''
    tell application "Calendar"
        tell calendar "Home"
            set newEvent to make new event with properties {{summary:"{title}", start date:date "{start_time}", end date:date "{end_time}"}}
    '''

    # Only add location if it's provided
    if location:
        script += f'\nset location of newEvent to "{location}"'

    # Only add notes if they're provided
    if notes:
        script += f'\nset description of newEvent to "{notes}"'

    # Close the AppleScript block
    script += '''
        end tell
    end tell
    '''

    # Run the AppleScript
    subprocess.run(["osascript", "-e", script])



# add_event_to_calendar("Meeting with John", "2024-09-11T09:00:00", "2024-09-11T10:00:00")
def draw_freeform():
    import turtle

    screen = turtle.Screen()
    screen.title("Draw Freeform")
    screen.setup(width=800, height=600)

    pen = turtle.Turtle()
    pen.speed(0)
    pen.pensize(2)

    def draw(x, y):
        pen.goto(x, y)

    screen.tracer(0)
    pen.penup()

    screen.onclick(pen.goto)
    turtle.listen()
    turtle.mainloop()

# draw_freeform()
def create_freeform_doodle():
    import subprocess
    subprocess.run(["open", "-a", "Freeform"])  # Opens Preview, where you can create a freeform doodle
# create_freeform_doodle()
def create_blank_canvas():
    import subprocess
    subprocess.run(["open", "-a", "Freeform", "--args", "--new-canvas"])
create_blank_canvas()
