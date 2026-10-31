import datetime
import sys

# I keep a fixed offset per city in this table instead of using a time
# zone database, so the offsets never adjust for daylight saving. That
# is a real limit of this program, not a detail: Boston at -4 is its
# daylight time, and in winter the real Boston is an hour behind what
# I print here. The table replaces a long if/elif chain that did the
# same job; one dict makes a missing city and a new city both obvious.
# Offsets are (hours, minutes) because Kolkata is not a whole hour.
CITY_OFFSETS = {
    "Boston": (-4, 0),
    "Tokyo": (9, 0),
    "Chicago": (-5, 0),
    "Seattle": (-7, 0),
    "Kolkata": (5, 30),
    "Karachi": (5, 0),
    "Cairo": (2, 0),
    "Shanghai": (8, 0),
}

# Built once, not per prompt: maps a folded name back to the spelling
# the table uses for the printed label.
_LOOKUP = {name.lower(): name for name in CITY_OFFSETS}


def time_for_city(city, now_utc):
    """Return (label, hour, minute, second) for city at now_utc.

    An unknown city is not an error in my program: it returns the UTC
    time with the label GMT, and the caller prints the "not added"
    line. The arithmetic goes through total minutes so the Kolkata
    half hour and the midnight wrap share one path; doing hour and
    minute separately is how this once printed 21:66.
    I lose the date on purpose: the result is a time of day only, and
    nothing in this program tracks which day it falls on.
    """
    offset = CITY_OFFSETS.get(city)
    if offset is None:
        return "GMT", now_utc.hour, now_utc.minute, now_utc.second
    total_minutes = now_utc.hour * 60 + now_utc.minute + offset[0] * 60 + offset[1]
    total_minutes %= 24 * 60
    return city, total_minutes // 60, total_minutes % 60, now_utc.second


def main():
    while True:
        try:
            city = input("Enter city: ")
        except EOFError:
            # Closed input ends the loop the same way typing exit
            # does. Before I caught this, piped input that ran out
            # raised EOFError and the program died with a traceback.
            break
        except KeyboardInterrupt:
            print()
            break

        # I match exit and city names after stripping and folding
        # case. The first version matched exactly, so "tokyo" and
        # " exit" fell through to the unknown city line, which read
        # as a bug to anyone typing normally. The table keys keep
        # their capital spelling for the printed label.
        stripped = city.strip()
        if stripped.lower() == "exit":
            break
        canonical = _LOOKUP.get(stripped.lower())
        if canonical is None:
            print(stripped, "is not added")
        # The base has to be UTC, not local time. I used datetime.now()
        # with no zone at first, and every city came out wrong by the
        # offset of the machine running it. I fetch it fresh each
        # round so a long session does not keep printing the time
        # from when it started. An unknown name passes through as
        # GMT inside time_for_city.
        label, hour, minute, second = time_for_city(
            canonical if canonical is not None else stripped,
            datetime.datetime.now(datetime.timezone.utc),
        )

        # Zero padded, because 8:5:3 is hard to read as a clock time
        # and padding costs nothing here.
        print(label, f"{hour:02d}:{minute:02d}:{second:02d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
