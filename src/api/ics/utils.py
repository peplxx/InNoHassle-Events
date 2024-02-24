import datetime

import icalendar
from icalendar import vDDDTypes

# TODO: Timezone
timezone = datetime.timedelta(hours=3)


async def make_deadline(event: icalendar.Event) -> icalendar.Event:
    description = event["DESCRIPTION"]
    end = event["DTEND"].dt
    date = end.date()
    begin = datetime.datetime(day=date.day, year=date.year, month=date.month)
    name = event["SUMMARY"]
    event["SUMMARY"] = "[DEADLINE] " + name
    event["DESCRIPTION"] = description + f"\n Due to: {(end - timezone).time()}"
    event["DTSTART"] = vDDDTypes(begin)
    return event


async def create_quiz(opens: icalendar.Event, closes: icalendar.Event) -> icalendar.Event:
    quiz_name = opens["SUMMARY"]
    opens["SUMMARY"] = "[QUIZ] " + quiz_name.split("opens")[0]
    opens["DTSTART"] = vDDDTypes(opens["DTSTART"].dt + timezone)
    opens["DTEND"] = vDDDTypes(closes["DTEND"].dt + timezone)
    return opens


async def add_course_tag(event: icalendar.Event):
    tag = (event["CATEGORIES"]).to_ical().decode(encoding="utf-8")
    course_name = tag.split("]")[1]
    event["DESCRIPTION"] = f"Course: {course_name}\n" + event["DESCRIPTION"]
