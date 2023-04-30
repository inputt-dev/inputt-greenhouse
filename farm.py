from datetime import timedelta, date
import pickle
import time

from GreenhouseEvent import *
from plants import *
from parameters import *
from animals import *
from farm import *
from Globals import Globals

"""
Crop farm, holds and manipulated the status of the crops and ranch animals
"""

class farm: #information about when plants are planted
	def __init__(self): #What and how many are planted
		startDate = date(2022, 4, 1)
		parameters = {"Start date": (startDate,"Start point in time of the greenhouse"),
					 "plantingArea": (150, "Available area for plants in sq M"),
					 "customers": ([], "List of all registered customers")
					 }
		self.parameters = Parameters(parameters)
		self.events = {} #{date: [GreenhouseEvent1, GreenhouseEvent2...]}
		self.areaUsed = 0

		#self.plantingMap = np.zeroes(s, dtype=int)
		#Now define the planting rows
		self.fileName = "events.grh" #For saving and loading crop plans
		self.PlantingEventID = 0#Each planting spawns a number of subsequent events, this id ties events to its original planting
		
		#Now add a start event, for this year 2022 to open greenhouse.  this will help to auto generate csv's that work easier with
		#the master excel spreadsheet
		openingEvent = GreenhouseEvent(startDate, None, 0)
		openingEvent.parameters.set("type",  "Greenhouse opening Day")
		self.trackChanges = 0 #Increment for every change done to the schedule
		self.addEvent(openingEvent)
		self.trackChanges = 0 #How many changes are done for the confirmExit function, reset back to zero after addEvent adds it
		self.PlantingEventID = 1

		#Create the plant dictionary with instances of every type defined in the program
		self.plants = []
		self.plants.append(IndeterminateTomatoes())
		self.plants.append(LongEnglishCucumbers())
		self.plants.append(CanaryBellPeppers())
		self.plants.append(CaliforniaWonderGreenBellPeppers())
		self.plants.append(Saskatoons())
		self.plants.append(IcebergLettuce())
		planted = IndeterminateTomatoes()
		plant_date = date(2023,6,6)
		total_plants = 100
		events = planted.getEvents(plant_date, total_plants)
		for event in events:
			event.parameters.set("ID", self.PlantingEventID)
			self.addEvent(event)
			self.PlantingEventID += 1 #Need a new unique planting event ID

		planted = CaliforniaWonderGreenBellPeppers()
		events = planted.getEvents(date(2023,3,3), 129)
		for event in events:
			event.parameters.set("ID", self.PlantingEventID)
			self.addEvent(event)
			self.PlantingEventID += 1 #Need a new unique planting event ID

	def __str__(self):
		begindate = self.parameters.get("Start date")
		ret = ""
		ret = ret + "Crop started on: " +  str(begindate) + "\n"
		ret = ret + "There are " +  str(len(self.events)) + " days that have events." +  "\n"
		for (k,v) in self.events.items():
			ret += str(k) + "" + "\n"
			for e in v: #A list of events on this day, represented by the key k.
				ret += "    " + str(e)
		return ret
	def summary(self): #At any given date show whats planted, and what needs harvesting today
		#From the beginning date, run through all the planting events until the last plant dies
		loopdate = min(self.events)
		enddate = max(self.events)
		profit = 0
		areaUsed = 0
		maxArea = 0
		plantingArea = self.parameters.get("plantingArea")
		ret = ""
		while loopdate <= enddate:
			if loopdate in self.events:
				todaysEvents = self.events[loopdate]
				print("Date: {}".format(loopdate))
				for e in todaysEvents:
					ret += "{}".format(e)
					profit += e.profit()
					areaUsed += e.areaChanged() #Track the total used
					maxArea = max(areaUsed, maxArea) #See how big the plantings get eventually
					utilizationRate = "{:.2%}".format(areaUsed/plantingArea)
					labour = e.labourCost()
					ret += e.csv() + "," + utilizationRate + "," + str(profit) + "," + str(labour) + "\n"
					if e.isHarvesting():
						print("{}".format(e))
					if e.isPlanting():
						print("{}".format(e))

			loopdate = loopdate + timedelta(days=1)
		return ret
	
	def get_plant(self, type):
		for plant in self.plants:
			if type == plant.parameters.get("type"):
				return plant
		return None

	#Returns a list of known plant names
	def plant_names(self):
		ret = []

		for p in self.plants:
			ret.append(p.parameters.get("type"))
		return ret
	
	def removePlanting(self):
		#loop through all planting dates, number them and query the user which one to remove
		loopdate = min(self.events)
		enddate = max(self.events)
		indexDict = {}
		index = 0
		self.trackChanges += 1 #more changes done
		while loopdate <= enddate:
			if loopdate in self.events:
				todaysEvents = self.events[loopdate]
				for e in todaysEvents:
					if e.type == "Planting":
						print (str(index) + ": " + str(e) + "\n")
						indexDict[index] = e #Numerate the plantings for the user
						index += 1
			loopdate = loopdate + timedelta(days = 1) #Keep scanning through every day for planting events
		selection = OneTouchInput("Selecting Planting to remove(Enter to cancel)")
		if selection == "\n":
			print("Cancelling...")
		else:
			selection = int(selection)
			if selection >= 0 and selection < index: #Within in range
				print("removing " +  str(selection))
				print(indexDict[selection])
				event = indexDict[selection] #Get the planting event the user select
				PlantingID = event.parameters.get("ID") #Now we have its ID we remove all events with this PlantingID
				for e in self.events:
					todaysEvents = self.events[e]
					newList = []
					for t in todaysEvents:
						if t.parameters.get("ID") == PlantingID: #This is the planting event or a subsequent action resulting from it
							print("removing " + str(t))
						else: #Reconstruct the list
							newList.append(t)
					#Now we have a new list, for this day with the PlantingID events not added
					self.events[e] = newList
			else:
				print("Selection out of range")

	def addEvent(self, event): #Add an event to this crops history
		startdate = event.parameters.get("dateActioned")
		self.trackChanges += 1 
		if startdate in self.events: #is there something happening that day?
			self.events[startdate].append(event)
		else: #Nothing this day, initialize the list and add it to the events dictionary
			self.events[startdate] = [event]

	def setGreenHouseSize(self):
		plantingArea = self.parameters.get("plantingArea")
		print("Current size = " + str(plantingArea) + "(sq/m). " +  "{:.2%}".format(plantingArea * 10.7639104) +  " square feet.")
		size = float(input("Set GreenHouse size in square meters."))
		self.parameters.set("plantingArea",size)
	def getAllHarvestEvents(self, eventlist): 
		#return a list of all harvests
		harvests = [] #a list of all the harvests, sorted by date

		for eventDate, eventsToday in eventlist.items():
			#For todays events see if any are type of planting
			for e in eventsToday:
				if e.isHarvesting() is True:
					harvests.append(e)
		return harvests

	def getAllPlantingEvents(self):
		plantings = [] #a list of all the harvests, sorted by date

		for eventDate, eventsToday in self.events.items():
			#For todays events see if any are type of planting
			for e in eventsToday:
				if e.isPlanting() is True:
					plantings.append(e)
		return plantings

	def enterPO(self):
		#List harvest dates and amounts available and freshness window to sell
		harvests = self.getAllHarvestEvents(self.events) #Collect all the harvest events
		harvested = enumerateAndSelect(harvests) #Prompt the user to select one
		maxAmount = harvested.maxToSell() #Get the maximum amount one can buy for this harvest
		customers = self.parameters.get("customers") #Get the buyer list
		customer = enumerateAndSelect(customers) #Prompt the user to select a buyer

		try:
			amount = getInteger("Purchase amount", 0, 0, maxAmount)
		except Exception as e:
			print("{}".format(e))
			print("Cancelling")
			return
		harvested.addPO(customer, amount)
		
	def save(self):
		print("Saving...")
		#Get the name of the file to save to, and then dump the crop object
		try:
			fileName = getFileName(self.fileName)
			#Hitting enter selects the default file name listed in the string
			f = open(fileName, "wb")
			#Save the crop object via pickle
			pickle.dump(self, f)
			f.close()
			self.trackChanges = 0 #These changes are now saved
		except:
			print("Exception  occured")
	def load(self):
		print("Loading...")
		#Get a list of files ending in *.grh, have the user select one
		fileName = enumeratedFileSelector("grh")

		f = open(fileName, "rb")
		c = pickle.load(f)
		c.trackChanges = 0 #Back to square one
		return c #A class to hold all the crops

	def confirmExit(self):  #See if theres been changes, if so wait 10 seconds for a keypress otherwise just exit
		#f self.trackChanges == 0:
		#	return
		#now wait 10 seconds for a keypress
		startTime = time.time()
		delay = 10 #10 seconds to wait before exiting program
		print("You have {} changes.  Hit S to save X to exit or wait 10 seconds to close".format(self.trackChanges))
		waitTime = 0 #Start the countdown!
		warned = False
		while waitTime < delay:
			if keyboard.is_pressed('S') or keyboard.is_pressed('s'): #User wants to save
				#wait until the key is released
				self.save()
				break
			if keyboard.is_pressed('X') or keyboard.is_pressed('x'):
				break
			currentTime = time.time()
			waitTime = currentTime-startTime
			if delay - waitTime < 5 and warned == False:
				print("Exiting in 5 seconds...")
				warned = True

	def settings(self):
		print("Set Parameters")
		print("1. Greenhouse")
		print("2. Plant library")
		print("3. Animals")
		print("4. Events")
		input = OneTouchInput("Selection")
		try:
			if input == "1":
				self.parameters.changeParameters()
			if input == "2":
				selection = enumerateAndSelect(self.plants) #Select the plant to change
				self.plants[selection].parameters.changeParameters() #Run the routine to change the parameter
			if input == "3":
				selection = enumerateAndSelect(self.animals) #Select the animal to change
				self.animals[selection].parameters.changeParameters() #Run the routine to change the parameter
			if input == "4":
				selection = enumerateAndSelect(self.events) #Gets the date selected from the list, with another list of events this day
				thisDaysEvents = self.events[selection]
				selection = enumerateAndSelect(thisDaysEvents) #Select the event from this date
				selection = thisDaysEvents[selection]
				selection.parameters.changeParameters() #Change the parameters of this event on this date
		except Exception as e:
			print("{}".format(e))
