import os
from typing import List

from booking_calendar import ApartmentCalendars
from ics import Calendar


def test_init():

    apartment_calendar = ApartmentCalendars()
    assert apartment_calendar.files == []
    assert apartment_calendar.added_dates == []
    assert apartment_calendar.date_range == []
    assert apartment_calendar.apartments_status == []
    assert apartment_calendar.final_list == []


# test when started in wrong folder
def test_get_cal_date_files_empty_folder():

    apartment_calendar = ApartmentCalendars()
    os.chdir("tests")
    apartment_calendar.get_cal_dates()
    assert apartment_calendar.files == []
    os.chdir("..")


# test when started in good folder and loads 5 calendars
def test_get_cal_date_files():

    apartment_calendar = ApartmentCalendars()
    apartment_calendar.get_cal_dates()
    sorted(apartment_calendar.files)
    assert sorted(apartment_calendar.files) == sorted(
        [
            "booking_cal_two.ics",
            "booking_cal_three.ics",
            "booking_cal_five.ics",
            "booking_cal_four.ics",
            "booking_cal_one.ics",
        ]
    )


def sort_date_lists(date_lists):

    new_list = []
    for apt in date_lists:
        new_list.append(sorted(apt, key=lambda a: a[0]))

    return sorted(new_list, key=lambda a: a[0][0])


def extract_date_list_from_calendars(calendars: List[Calendar]):

    apartment_date_list = []
    for calendar in calendars:
        date_list = []
        for event in calendar.events:
            event_dates = [event.begin.date(), event.end.date()]
            date_list.append(event_dates)

        apartment_date_list.append(date_list)
    return sort_date_lists(apartment_date_list)


def test_get_cal_date_added_dates():

    apartment_calendar = ApartmentCalendars()
    apartment_calendar.get_cal_dates()
    calendars = []
    for file in apartment_calendar.files:
        data = open(file, "r")
        calendars.append(Calendar(data.read()))
        data.close()
    expected = extract_date_list_from_calendars(calendars)
    assert sort_date_lists(apartment_calendar.added_dates) == expected
