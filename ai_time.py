import datetime

# The whole program is this one loop. I keep a fixed offset per city in
# the branch chain below instead of using a time zone database, so the
# offsets never adjust for daylight saving. That is a real limit of this
# program, not a detail: Boston at -4 is its daylight time, and in
# winter the real Boston is an hour behind what I print here.

while (True):
  try:
    city = input("Enter city: ")
  except EOFError:
    # Closed input ends the loop the same way typing exit does. Before
    # I caught this, piped input that ran out raised EOFError and the
    # program died with a traceback instead of just stopping.
    break

  # I check for exit before I fetch the time, and the match is exact.
  # "Exit" or " exit" do not quit here; they fall through and get
  # treated as unknown cities below.
  if city == "exit":
    break

  # The base has to be UTC, not local time. I used datetime.now() with
  # no zone at first, and every city came out wrong by the offset of
  # the machine running it. The offsets below are all counted from
  # UTC, so the base has to be UTC too. I fetch it fresh each round so
  # a long session does not keep printing the time from when it
  # started.
  current_time = datetime.datetime.now(datetime.timezone.utc)
  # I do the offset math on plain hour and minute ints by hand and fix
  # the result up afterwards, below the chain. The second never needs
  # touching because no offset in the chain has a seconds part.
  hour = current_time.hour
  minute = current_time.minute
  second = current_time.second

  # Each branch is an exact, case sensitive name match, so "tokyo"
  # lands in the else at the bottom. The branches cannot overlap, so
  # their order here does not change any result.
  if city == "Boston":
    hour = hour - 4

  elif city == "Tokyo":
    hour = hour + 9

  elif city == "Chicago":
    hour = hour - 5

  elif city == "Seattle":
    hour = hour - 7

  elif city == "Kolkata":
    # Kolkata is the one half hour offset in the chain. Adding 30 to
    # the minute can push it past 59 on purpose; the fix up lines after
    # the chain carry that into the hour. This branch is wrong without
    # those lines, which is how it printed 21:66 before I added them.
    hour = hour + 5
    minute = minute + 30

  elif city == "Karachi":
    hour = hour + 5

  elif city == "Cairo":
    hour = hour + 2

  elif city == "Shanghai":
    hour = hour + 8

  ## A new city goes in as an elif above this else. The else is the
  ## catch all, so anything placed after it never runs.

  else:
    # An unknown city is not an error in my program. I say it is not
    # added, then I reuse the city variable as the label for the print
    # below and show the UTC time unchanged. Nothing above touched the
    # hour or minute on this path, so what prints really is UTC.
    print(city, "is not added")
    city = "GMT"

  # These three lines have to run after the chain, and in this order.
  # First the minute overflow carries into the hour, then the minute
  # wraps, then the hour wraps. Python floor division and modulo
  # handle the negative side too, so Boston at 01:10 UTC gives hour
  # -3 here and comes out as 21, the previous evening. I lose the
  # date at this line on purpose: the wrap keeps a time of day only,
  # and nothing in this program tracks which day the result falls on.
  hour = hour + minute // 60
  minute = minute % 60
  hour = hour % 24

  # I join the numbers with str() and no padding, so 8:5:3 is what a
  # time like that actually prints as. That is the output shape this
  # program has always had and I left it alone.
  print(city, str(hour) + ":" + str(minute) + ":" + str(second))
