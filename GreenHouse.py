from Inputt import Inputt
from Globals import Globals
from workerthreads import threads, workerThread, stopWatchStart, stopWatchStop, stopWatchStartTime
from Greenhouse_db import Greenhouse_DB
from farm import *

"""
Global variables
"""
inputt = Inputt() 
db = Greenhouse_DB("create_db.sql")
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

def plantings():
	return [farm.summary()]

def add_planting():
	ret = []
	#Add a planting action and auto add the harvesting dates based on the plant type
	plants = farm.plant_names()
	plant_planted = inputt.enumerateAndSelect(plants)
	if plant_planted:
		planted = farm.get_plant(plant_planted)
		plant_date = inputt.get_date("Enter planting or harvesting date YYYY-MM-DD:", date(2023,4,1), date(2024,4,1), date(2023,5,1))
		if plant_date:
			total_plants = inputt.getInteger("How many plants?", 0, 99999, 100)
			if total_plants:
				#Call the plant objects get event function to map out all processing steps from planting to sale ready
				#This will add and date monies spent and monies earned
				#Add the planting event in, tagged with the current planting event id
				growtime = int(planted.parameters.get("growtime"))
				options = ["set date as harvest time", "set date as planting time"]
				option = inputt.enumerateAndSelect(options)
				if option:
					if option == "set date as harvest time":
						plant_date = plant_date + timedelta(days = -growtime)
					events = planted.getEvents(plant_date, total_plants)
					for event in events:
						event.parameters.set("ID", farm.PlantingEventID)
						farm.addEvent(event)
					farm.PlantingEventID += 1 #Need a new unique planting event ID
					ret.append(f"{total_plants} {plant_planted}s planted on {plant_date}")
				else:
					ret.append("Planting cancelled")
			else:
				ret.append(f"0 plants added on {plant_date}. Planting cancelled")
		else:
			ret.append("No date selected, planting cancelled")
	else:
		ret.append("No plant selected to plant, planting cancelled")
	inputt.menuLevel = ['1']
	return ret

def remove_planting():
	ret = []

	farm.trackChanges += 1 #more changes done
	plantings = farm.getAllPlantingEvents()
	planting_selection = inputt.enumerateAndSelect(plantings)
	if planting_selection:
		ret.append(f"removing {planting_selection}")
		PlantingID = planting_selection.parameters.get("ID") #Now we have its ID we remove all events with this PlantingID
		for today, todays_events in farm.events.items():
			newList = []
			for t in todays_events:
				if t.parameters.get("ID") == PlantingID: #This is the planting event or a subsequent action resulting from it
					ret.append(f"removing {t}")
				else: #Reconstruct the list
					newList.append(t)
		#Now we have a new list, for this day with the PlantingID events not added
		farm.events[today] = newList
	else:
		ret.append("No plantings removed")
	inputt.menuLevel = ['1']
	return ret

def export_to_csv():
	ret = []
	try:
		fileName = inputt.getString("Export work schedule CSV.", "work_schedule.csv")
		workScheduleFile= open(fileName,"w+")

		fileName = inputt.getString("Export monthly cost and income breakdown CSV", "money.csv")
		monthlyFile = open(fileName,"w+")

		fileName = inputt.getString("plant library", "plants.csv")
		plantsFile = open(fileName,"w+")
		ret =+ [workScheduleFile, monthlyFile, plantsFile]
		#Format a header line
		line = "Action Type,Date,Action Target,Size,Cost,Greenhouse Utilization(%),total Profit($),labour(h)\n"
		workScheduleFile.write(line)
		areaUsed = 0
		maxArea = 0

		profit = 0
		plantingArea = farm.parameters.get("plantingArea")

		#Run the csv export from the earliest event date to the last one
		loopdate = min(farm.events)
		enddate = max(farm.events)

		while loopdate <= enddate:
			if loopdate in farm.events:
				todaysEvents = farm.events[loopdate]
				for e in todaysEvents:
					profit += e.profit()
					areaUsed += e.areaChanged() #Track the total used
					maxArea = max(areaUsed, maxArea) #See how big the plantings get eventually
					utilizationRate = "{:.2%}".format(areaUsed/plantingArea)
					labour = e.labourCost()
					line = e.csv() + "," + utilizationRate + "," + str(profit) + "," + str(labour) + "\n"
					workScheduleFile.write(line)
			loopdate = loopdate + timedelta(days=1)
		
		#Now write lines adding up monthly totals for costs and income
		#Build two dictionary Cost = {(month, year): total} and Income = {(month,year): total}
		Cost = {} #Dictionaries to hold the monthly income,costs and labour total
		Income = {}
		Labour = {}
		loopdate = min(farm.events)
		enddate = max(farm.events)
		line = ""

		while loopdate <= enddate:
			month = loopdate.month
			year = loopdate.year
			index = (month, year)
			if index not in Income:
				Income[index] = 0
			if index not in Cost:
				Cost[index] = 0
			if index not in Labour:
				Labour[index] = 0

			if loopdate in farm.events:
				todaysEvents = farm.events[loopdate]
				for e in todaysEvents:
					profit = e.profit()
					if profit > 0: #add the income to the income dictionary
						Income[index] += profit
					else:
						Cost[index] += profit
					Labour[index] += e.labourCost()

			loopdate = loopdate + timedelta(days=1)
		#Now write out the month by month cost and income
		#CSV format month, year
		line = "month,year,Income,Cost,Labour\n"
		monthlyFile.write(line)
		for key in Income:
			month = str(key[0]) #The key is (month,year)
			year = str(key[1])
			income = str(Income[key])
			cost = str(Cost[key])
			labour = str(Labour[key])
			line = month + "," + year + "," + income + "," + cost + "," + labour + "\n"
			monthlyFile.write(line)
		
		#Now output the plant library CSV
		line = ""
		count = 0
		for k,v in farm.plants.items():
			if count == 0:
				line += v.toCSVHeader()
				count = 1
			line += v.toCSV()

		plantsFile.write(line)

		plantsFile.close()
		#Now write out the Income and Cost
		monthlyFile.close()
		workScheduleFile.close() #Done writing work schedule file
	except Exception as e:
		ret += [f'{e}']
	return ret


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
inputt.add_menu_item(['1'], name = "Plantings", func = plantings) 
inputt.add_menu_item(['1','1'], name = "Add planting", func = add_planting)
inputt.add_menu_item(['1','2'], name = "Remove planting", func = remove_planting)
inputt.add_menu_item(['2'], name = "Export to CSV", func = export_to_csv)
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
	userInput = inputt.next_line()

inputt.stop_threads()
