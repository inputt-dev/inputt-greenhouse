from Inputt import Inputt
from Globals import Globals
from workerthreads import threads, workerThread, stopWatchStart, stopWatchStop, stopWatchStartTime
from Greenhouse_db import Greenhouse_DB
from farm import *


"""
Global variables
"""
inputt = Inputt() 
db = Greenhouse_DB()
farm = farm()
Globals.set("farm", farm)
Globals.set("db", db)
Globals.set("inputt", inputt)

"""
Define the menu option functions
"""
#[] Load all the books from the library, and select one to start creating/reading it
def root():
	ret = ["Planting Calculator"]
	ret.append("Enter plants, date and number")
	ret.append("Then adjust its parameters as necessary")
	ret.append("Then the program will output the daily dashboard")
	return ret
def add_planting():
	#Add a planting action and auto add the harvesting dates based on the plant type
	plant_date =inputt.get_date("Enter planting or harvesting date YYYY-MM-DD:", date(2023,4,1), date(2024,4,1), date(2023,5,1))
	total_plants = inputt.getInteger("How many plants?", 0, 99999, 100)
	plant_names = []
	for index, plants in enumerate(farm.plants):
		plant_names.append(plants.parameters.get("type"))
		
	planted = inputt.enumerateAndSelect(plant_names)
	planted = farm.plants[planted]
	#Call the plant objects get event function to map out all processing steps from planting to sale ready
	#This will add and date monies spent and monies earned
	#Add the planting event in, tagged with the current planting event id
	growtime = int(planted.parameters.get("growtime"))
	options = ["set date as harvest time", "set date as planting time"]
	option = inputt.enumerateAndSelect(options)
	if option == "set date as harvest time":
		harvest_date = plant_date
		plantdate = plant_date + timedelta(days = -growtime)
	else:
		harvest_date = plant_date + timedelta(days = growtime)
	events = planted.getEvents(plantdate, total_plants)
	for event in events:
		event.parameters.set("ID", farm.PlantingEventID)
		farm.addEvent(event)
	farm.PlantingEventID += 1 #Need a new unique planting event ID
	plant_name = planted.parameters.get("type")
	return [f"{total_plants} {plant_name}s planted on {plant_date}"]

def removePlanting():
	#loop through all planting dates, number them and query the user which one to remove
	loopdate = min(farm.events)
	enddate = max(farm.events)
	indexDict = {}
	index = 0
	farm.trackChanges += 1 #more changes done
	while loopdate <= enddate:
		if loopdate in farm.events:
			todaysEvents = farm.events[loopdate]
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

def settings():
	ret = farm.summary()
	return [ret]

def plant_library():
	ret = inputt.enumerateAndSelect(farm.plants)
	return [ret]

def edit_settings():
	return ["Settings"]
"""
Define the menu hierarchy and supply the functions that go with each
"""
inputt.add_menu_item([], name = "Planting calculator", func = root)
inputt.add_menu_item(['1'], name = "Add planting", func = add_planting)
inputt.add_menu_item(['2'], name = "Remove planting", func = farm.removePlanting)
inputt.add_menu_item(['3'], name = "Enter purchase order", func = farm.removePlanting)
inputt.add_menu_item(['s'], name = "Farm settings", func = settings)
inputt.add_menu_item(['s', '1'], name = "Edit settings", func = edit_settings)
inputt.add_menu_item(['s', 'l'], name = "Load Farm", func = farm.save)
inputt.add_menu_item(['s', 's'], name = "Save Farm", func = farm.load)
inputt.add_menu_item(['s', '1'], name = "Plant library", func = plant_library)


inputt.add_menu_item(['x'], name = "Export to CSV", func = farm.exportCSV)


"""
The main loop, the program starts by automatically processing the base menu, or the empty list []
which has been defined with add_menu_item 
"""
inputt.startGui()
while True:
	db.flush_command_buffer()
	inputt.outputt()
	if inputt.endProgram:
		break
	userInput = inputt.nextLine()

inputt.stop_threads()
