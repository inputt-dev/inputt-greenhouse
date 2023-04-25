from parameters import Parameters

Globals = Parameters({}) #Create a blank parameters object

def status():
	farm = Globals.get("farm")
	inputt = Globals.get("inputt")
	num_plants = len(farm.plants)
	num_events = 0
	for date, events in farm.events:
		num_events += len(events)
	inputt.updateMenuItem([], f"Planting calculator: {num_plants} plants - {num_events} events)")
