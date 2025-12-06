from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
from drafter.llm import *
from meta import *

set_gemini_server("https://bitter-pine-ee21drafter-gemini-proxy.subibask.workers.dev")

# hide_debug_information()
# set_website_framed(False)
set_website_title("Your Drafter Website")
set_site_information(
    "author",
    """
Your description can go here.
""",
    [],
    [],
    [],
)

@dataclass
class Event:
    title: str
    date: str
    location: str
    description: str

@dataclass
class State:
    events: list[Event]
    bookmarks: list[int]
    calender: list[Event]
    pending_event: Event = None
    pending_text: str

@route
def index(state: State) -> Page:
    return Page(state, ["Hello ___!"])

@route
def upload_poster(state: State) -> Page:
    return Page(
        state, content = [
            Header("Upload Event Poster!"),
            FileUpload("poster"),
            Button("Create Event!", "extract_event_info"),
        ])

def parse_event_text(text:str) -> Event:
    title = ""
    date = ""
    location = ""
    description = ""

    lines = text.split("\n")
    for line in lines:
        if line.startswith("Title:"):
            title = line[len("Title:"):].strip()
        elif line.startswith("Date:"):
            date = line[len("Date:"):].strip()
        elif line.startswith("Location:"):
            location = line[len("Location:"):].strip()
        elif line.startswith("Description:"):
            description = line[len("Description:"):].strip()
    return Event(title, date, location, description)

@route
def extract_event_info(state:State, poster:bytes) -> Page:
    prompt = (
        "You are reading an event poster"
        "Extract ONLY the following information in plain text"
        "Ensure that the date extracted is in MM/DD format"
        "Title:\nDate:\nLocation:\nDescription:"
    )
    
    result_text = call_gemini(
        image=poster,
        prompt=prompt)

    event = parse_event_text(result_text)

    state.pending_event = event
    return Page(
       state, content = [
           Text("Here's the information Gemini collected:"),
           f"{event}",
           Text("Is this correct?"),
           Button("Yes", "save_event"),
           Button("Edit", "preview_event")
       ])

@route
def preview_event(state: State) -> Page:
    return Page(state, content=[
        Header("Event Details:"),
        TextBox("title", event.title),
        TextBox("date", event.date),
        TextBox("location", event.location),
        TextBox("description", event.description),
        Button("Save Information", "save_event_corrected")
    ])

@route
def save_event_corrected(state: State, title, date, location, description) -> Page:
    event = Event(title, date, location, description)
    state.events.append(event)
    return index(state)

@route
def save_event(state: State, event: Event) -> Page:
    state.events.append(event)
    return index(state)
    
start_server(State())
