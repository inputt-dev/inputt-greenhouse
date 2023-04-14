from Inputt import Inputt
from Globals import Globals
from workerthreads import threads, workerThread, stopWatchStart, stopWatchStop, stopWatchStartTime
from Greenhouse_db import Greenhouse_DB
from farm import *


"""
create the inputt and database variables
"""
inputt = Inputt() 
db = Greenhouse_DB()
farm = farm()
Globals.set("book", farm)
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

def settings():
	ret = farm.summary()
	return [ret]

def plant_library():
	ret = inputt.enumerateAndSelect(farm.plants)
	return [ret]

"""
Define the menu hierarchy and supply the functions that go with each
"""
inputt.add_menu_item([], name = "Planting calculator", func = root)
inputt.add_menu_item(['1'], name = "Add planting", func = farm.addPlanting)
inputt.add_menu_item(['2'], name = "Remove planting", func = farm.removePlanting)
inputt.add_menu_item(['3'], name = "Enter purchase order", func = farm.removePlanting)
inputt.add_menu_item(['2'], name = "Remove planting", func = farm.removePlanting)
inputt.add_menu_item(['s'], name = "Farm settings", func = settings)
inputt.add_menu_item(['s', '1'], name = "Edit settings", func = farm.summary)
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
