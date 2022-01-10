# Holiday_Manager
This is the holiday mangement application that gathers holidays information from https://www.timeanddate.com/calendar/print.html?year=2022&country=1&cols=3&hol=33554809&df=1 .
There is an option to manually add holidays to the file.
There is also option to remove holidays from the file.
You can view the list of holidays by entering the year and week number. For the current weeek there is even an option to view weather information. The weather information is retrieved from https://rapidapi.com/weatherapi/api/weatherapi-com/

# Installation Guide
Only Holiday_Manager.py and holidays.json are required. But both of these file needs to be in same location.

# Module needed
json, beautifulsoup, requests, dataclass, datetime, and os

# Some Note on week number
week 1 starts with the 1st Monday of the year. So, week 0 consist of the days before 1st Monday of the year.