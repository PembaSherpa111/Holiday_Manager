from datetime import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import os
import ignore

@dataclass
class Holiday:
    name : str
    date : datetime.date      
    
    def __repr__ (self):
        return "%s (%s)" % (self.name , self.date)

class HolidayList():
    """HolidayList Class"""
    def __init__(self):
       self.innerHolidays = []

    def addHoliday(self,holidayObj): #adds holidayObj to innerHolidays
        if isinstance(holidayObj,Holiday) == False:         # Make sure holidayObj is an Holiday Object by checking the type
            print("Error : holidayObj is of incorrect type.")
        else:
            if self.findHoliday(holidayObj.name, holidayObj.date) == True: # if the holiday already exist, it doesn't append
                print(f"Error: \n {holidayObj} already exist.")
            else:
                self.innerHolidays.append(holidayObj)
                print(f"Success:\n {holidayObj} has been added to the holiday list.")
                self.changes_exist() #pointing out there is a change in data  

    def findHoliday(self,HolidayName, date): # checks if the HolidayName exist in innerHolidays and returns True or False
        holiday = list(filter(lambda holiday: holiday.name == HolidayName and holiday.date == str(date), self.innerHolidays)) #filters innerholidays by the HolidayName and date
        if len(holiday) > 0: 
            return True
        else:
            return False

    def removeHoliday(self,HolidayName): #removes holiday by name
        holiday = list(filter(lambda holiday: holiday.name == HolidayName, self.innerHolidays)) #checking if HolidayName exist
        if len(holiday) > 0:
            self.innerHolidays = list(filter(lambda holiday: holiday.name != HolidayName, self.innerHolidays))
            print(f"Success:\n {HolidayName} has been removed from the holiday list.")
            self.changes_exist()  #pointing out there is a change in data 
        else:
            print(f"Error: \n {HolidayName} not found")
    
    def read_json(self):
        with open("holidays.json", "r") as reader:
            holidays_json = json.load(reader) #holidays is a dictionary with value as list of dictionary
            if len(holidays_json) > 0: #checking if json is empty
                holidays_list = holidays_json["holidays"] #"holidays" is key
                for i in range(0,len(holidays_list)):
                    name = holidays_list[i]["name"]
                    date = holidays_list[i]["date"]
                    if self.findHoliday(name, date) == False:
                        holidayObj = Holiday(name,date)
                        self.innerHolidays.append(holidayObj) 
                        # self.addHoliday(holidayObj) can also be used 
    
    def save_to_json(self):
        holidays_list = []
        for i in range(0,len(self.innerHolidays)):
            holidayObj = self.innerHolidays[i]
            holiday = {"name": holidayObj.name, "date" : f"{holidayObj.date}"}
            holidays_list.append(holiday)
        holidays_json = {"holidays" : holidays_list} #formatiing to required json format
        with open("holidays.json", "w") as writer:
            json.dump(holidays_json,writer)
        print("\nSuccess:\nYour changes have been saved.")
        global changes_exist
        changes_exist = False #pointing out the existing changes have been saved and no further changes exist
        self.read_json()

    def scrapeHolidays(self):
        current_year = datetime.today().year
        year_list =[current_year-2,current_year-1,current_year,current_year+1,current_year+2] #2 previous years, current year, and 2  years into the future
        for i in range(0,len(year_list)):
            year = str(year_list[i])
            base_url = "https://www.timeanddate.com/calendar/print.html?year="+ year + "&country=1&cols=3&hol=33554809&df=1"
            html = requests.get(base_url).text
            soup = BeautifulSoup(html,"html.parser")
            table = soup.find("table", class_= "cht lpad")
            for row in table.find_all("tr"):
                column = row.find_all("td")
                date_string = f"{column[0].string}, {year}"
                date = datetime.strptime(date_string,"%b %d, %Y").date() #string to datetime
                name = column[1].string
                if self.findHoliday(name, date) == False: #if holidayObj doesn't already exist 
                    holidayObj = Holiday(name, date)
                    self.addHoliday(holidayObj)
                    save = "a" # random value which is not y or n
        try: 
            if save == "a":
                while save.lower() not in ["y","n"]: #asking if saving is required as new holidays were scraped from the web
                    save = input("\n New holiday data found. Do you want to save them? [y/n]: ")
                if save.lower() == "y":
                    self.save_to_json()
                else:
                    self.changes_exist() #pointing out there is a change in data
        except:
            pass   

    def numHolidays(self):
        print(f"There are {len(self.innerHolidays)} holidays stored in the system.") # Return the total number of holidays in innerHolidays

    def filter_holidays_by_week(self, year, week_number):
        week_day = [1,2,3,4,5,6,0] # 1-mon, 2-tues ... 0-sun
        date = list(map(lambda day: datetime.strptime(f"{year}-{week_number}-{day}", "%Y-%W-%w").date() ,week_day)) #creating list of date in the given week and year
        date = [str(day) for day in date] #converting datetime.date type to str
        holidays = list(filter(lambda holidays: holidays.date in date ,self.innerHolidays )) #filtering holidays by date
        return holidays

    def displayHolidaysInWeek(self,year, week_number):
        holidays = self.filter_holidays_by_week(year, week_number)
        if len(holidays) > 0:
            print(f"\nThese are the holidays for {year} week #{week_number}: ")
            for i in range(0,len(holidays)):
                print(f"{holidays[i]}")
        else:
            print(f"\nThere are no holidays in {year} week #{week_number}")

    def getWeather(self,year,week_number):
        week_day = [1,2,3,4,5,6,0] # 1-mon, 2-tues ... 0-sun
        date = list(map(lambda day: datetime.strptime(f"{year}-{week_number}-{day}", "%Y-%W-%w").date() ,week_day)) #creating list of date in the given week and year
        url = "https://weatherapi-com.p.rapidapi.com/history.json"
        dt = date[0]
        end_dt =date[-1]
        querystring = {"q":"Milwaukee,US","dt":f"{dt}","lang":"en","end_dt":f"{end_dt}"}
        headers = {
            'x-rapidapi-host': "weatherapi-com.p.rapidapi.com",
            'x-rapidapi-key': ignore.key
            }
        response = requests.request("GET", url, headers=headers, params=querystring).json()
        weather = response["forecast"]["forecastday"]
        date_weather = []
        for i in range(0,len(weather)):
            date = weather[i]["date"]
            condition =  weather[i]["day"]["condition"]["text"]
            date_weather.append({"date": f"{date}", "condition" : f"{condition}" })
        return date_weather

    def viewCurrentWeek(self): #shows the data on present day and upcoming 6 days
        year, week_num, week_day = datetime.today().isocalendar()
        holidays = self.filter_holidays_by_week(year, week_num)

        see_weather = "a" #random value which is not y or n
        while see_weather.lower() not in ["y","n"]:
            see_weather = input("Would you like to see this week's weather? [y/n]: ")
        if see_weather.lower() == "y":
            weather = self.getWeather(year, week_num)
            if len(holidays) > 0: #checking id any holiday exist
                date_of_holidays = [holidays[i].date for i in range(0,len(holidays))] #need holidays date to filter out weather date
                weather = list(filter(lambda weather: weather["date"] in date_of_holidays, weather))
                print(f"\nThese are the holidays for this week: ")
                for i in range(0,len(holidays)):
                    holiday = holidays[i]
                    weather_list = list(filter(lambda weather: weather["date"] == holiday.date, weather)) #filtering weather detail by holiday date
                    try:
                        weather_condition = weather_list[0]["condition"]
                    except:
                        weather_condition = "weather data not available"
                    print(f"{holiday} - {weather_condition}")
            else:
                print("There are no holidays this week.")
        else:
            if len(holidays) > 0: #checking id any holiday exist
                print(f"\nThese are the holidays for this week: ")
                for i in range(0,len(holidays)):
                    print(f"{holidays[i]}")
            else:
                print("There are no holidays this week.")

    def changes_exist(self):
        global changes_exist
        changes_exist = True

def main_menu():
    print("\nHoliday Menu","================","1. Add a Holiday","2. Remove a Holiday","3. Save Holiday List","4. View Holidays","5. Exit", sep=os.linesep)
    menu = input("Pick an option from the menu. Enter 1, 2, 3, 4 or 5: ")
    while menu not in ["1","2","3","4","5"]:
        menu = input("Invalid input. Enter 1, 2, 3, 4 or 5: ") 
    return menu   

def menu_1():
    print("\nAdd a Holiday\n============================")
    name = input("Holiday: ")
    date_string = input("Date: ")
    valid_date = False
    while valid_date == False:
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d").date()
            holidayObj = Holiday(name,date)
            Holidayschedule.addHoliday(holidayObj)  
            valid_date = True
        except ValueError:
            print("\nError:\nInvalid date. Please try again with the format: YYYY-MM-DD.")
            date_string = input(f"\nDate for {name}: ")

def menu_2():
    print("\nRemove a Holiday\n===========================")
    name = input("Holiday name: ")
    Holidayschedule.removeHoliday(name)

def menu_3():
    print("\nSaving Holiday List\n========================")
    save = "a" # random value which is not y or n
    while save.lower() not in ["y","n"]:
        save = input("Are you sure you want to save your changes? [y/n]: ")
    if save.lower() == "y": 
        Holidayschedule.save_to_json()
    else: 
        print("\nCanceled:\nHoliday list file save canceled.")

def menu_4():
    print("\nView Holidays\n============")
    
    invalid_input = True
    while invalid_input == True: #input value for year must be integer
        try:
            year = int(input("Which year? "))
            if len(str(year)) == 4:
                invalid_input = False
            else:
                print("Invalid Year. Please enter the year in the format YYYY.")
        except:
            print("Invalid input. The format of the year is YYYY.")

    invalid_input = True
    week_number = input("Which week? #[0-52, Leave blank for the current week]: ") #weeek 0 is the days before 1st monday of the year
    while invalid_input == True:
        try:   
            if len(str(week_number)) == 0:
                invalid_input = False
            elif int(week_number) in range(0,53):
                invalid_input = False
            else:
                week_number = input("Invalid week number. Enter integer between 0 and 52 or leave blank for current week.\nWhich week? #[0-52, Leave blank for the current week]: ")
        except:
            if invalid_input == True:
                week_number = input("Invalid week number. Enter integer between 0 and 52 or leave blank for current week.\nWhich week? #[0-52, Leave blank for the current week]: ")

    if len(str(week_number)) == 0:
        Holidayschedule.viewCurrentWeek()
    else:
        Holidayschedule.displayHolidaysInWeek(year, week_number)

def menu_5():
    print("\nExit\n============")
    exit = False
    if changes_exist == True:
        end = "a" #random value which is not y or n
        while end.lower() not in ["y","n"]:
            end = input("Are you sure you want to exit?\nYour changes will be lost.\n[y/n]: ")
        if end == "y":
            print("Goodbye !")
            exit = True
    elif changes_exist == False:
        end = "a" #random value which is not y or n
        while end.lower() not in ["y","n"]:
            end = input("Are you sure you want to exit? [y/n]: ")
        if end == "y":
            print("Goodbye !")
            exit = True
    return exit

def main(): 
    global Holidayschedule
    Holidayschedule = HolidayList() #initializing
    Holidayschedule.read_json()
    global changes_exist
    changes_exist = False
    Holidayschedule.scrapeHolidays()
    exit = False
    while exit == False:
        print("\nHoliday Manager\n=============================")
        Holidayschedule.numHolidays()
        menu = main_menu()
        if menu == "1":
            menu_1()
        elif menu =="2":
            menu_2()
        elif menu == "3":
            menu_3()
        elif menu == "4":
           menu_4()
        elif menu == "5":
           exit = menu_5()

# main()
if __name__ == "__main__":
    main();