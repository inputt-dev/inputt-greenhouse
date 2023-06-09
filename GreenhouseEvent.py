from parameters import *

"""
Greenhouse events: an action that happens in the greenhouse
"""
class GreenhouseEvent: #A class to hold all the information about planting, harvesting, fertilizing, pesticide and other jobs
	def __init__(self, start, object, size):
		p =	{"type": ("Base Class", "Base Greenhouse Event"),
			"dateActioned": (start, "Day Event Started"),
			"actionObject": (object, "The Object of the event"),
			"size": (size, "How many objects it affects"),
			"ID": (0, "The identifier of the creation event that spawned this event. Autogenerated, do not change"),
			"labour": (0, "How many hours it takes to finish this event"),
			"duration": (1, "How many days you have to finish this event once it starts"),
			"cost": (0, "The cost per plant of this event"),
			"totalCost": (0, "How much this event costs"),
			"nextID": (0, "The next unique planting ID")
			}
		self.parameters = Parameters(p)

	def __str__(self):
		dateActioned = self.parameters.get("dateActioned")
		size = self.parameters.get("size")
		eventType = self.parameters.get("type")
		actionObject = self.parameters.get("actionObject")
		if actionObject == None: #Special case for an event that has no plant object, ie open the greenhouse
			ret = "Opening greenhouse on " + str(dateActioned)
		else:
			objectName = actionObject.parameters.get("type")
			ret = "{} {} {} plants on {}".format(eventType,size,objectName, dateActioned)
		return ret
	def csv(self):
		eventType = self.parameters.get("type")
		dateActioned = self.parameters.get("dateActioned")
		size = self.parameters.get("size")
		actionObject = self.parameters.get("actionObject")

		if actionObject == None: #Special case for an event that has no plant object, ie open the greenhouse
			ret = eventType+","+str(dateActioned)+",Opening Greenhouse,"+str(size)+","+str(self.profit())
		else:
			objectType = actionObject.parameters.get("type")
			return "{},{},{},{},{}".format(eventType,dateActioned,objectType,size,self.profit())
		return ret
	def profit(self):
		return 0
	def areaChanged(self): #Planting area doesnt change by default, unless a plants being added or removed
		return 0
	def result(self): #The output of the event, by default nothing is produced, just a change in money but physical objects are the same
		return None
	def labourCost(self):
		labour = self.parameters.get("labour")
		size = self.parameters.get("size")
		return labour * size
	def isHarvesting(self):  #Define as true for later classes
		return False
	def isPlanting(self):
		return False

class Planting(GreenhouseEvent): #A planting event in the greenhouse
	def __init__(self, start, object, size):
		super().__init__(start, object, size)
		self.parameters.set("type", "Planting")
		self.parameters.set("labour",  1/60)
	def profit(self):
		size = self.parameters.get("size")
		return size * -1 #Default to one dollar per plant planting cost
	def areaChanged(self):
		size = self.parameters.get("size")
		actionObject = self.parameters.get("actionObject")
		return size * actionObject.area() #A plant starts growing
	def isPlanting(self):
		return True
	def __str__(self):
		return super().__str__()
	
class Harvesting(GreenhouseEvent): #A harvesting event in the greenhouse
	def __init__(self, start, object, size):
		super().__init__(start,object,size)
		self.parameters.set("type", "Harvesting")
		self.parameters.set("labour", 5/60)
		self.parameters.set("cost", -1)
	def profit(self):
		actionObject = self.parameters.get("actionObject")
		size = self.parameters.get("size")
		return actionObject.profit() * size

	def isHarvesting(self):
		return True

	def result(self): #Returns the output of the harvest, the unit of account in the profit calculation
		yieldrate = self.actionObject.parameters.get("yieldrate") #What each plant yields
		size = self.parameters.get("size")
		harvestOutput = yieldrate * size
		return harvestOutput #Salable produce is removed from the growing plant
	def yieldAmount(self): #How many units are produced
		yieldrate = self.actionObject.parameters.get("yieldrate")
		size = self.parameters.get("size")
		numberOfPlants = size
		yieldTotal = yieldrate * numberOfPlants
		return yieldrate * size
	def plantType(self): #What plant is being harvested
		return self.actionObject.parameters.get("type")
class PlantDeath(GreenhouseEvent):
	def __init__(self, start, object, size):
		super().__init__(start, object, size)
		self.parameters.set("type", "Removing")
		self.parameters.set("labour", 5/60)
	def profit(self):
		size = self.parameters.get("size")
		return size * -0.25 #Default to one quarter per plant removal cost
	def areaChanged(self):
		actionObject = self.parameters.get("actionObject")
		size = self.parameters.get("size")
		return size * actionObject.area() * -1 #Remove the plants from the greenhouse

class Processing(GreenhouseEvent): #A process is conducted on the
	def __init__(self, start, object, size, cost, labourhours):
		super().__init__(start, object, size) #Set the default values
		self.parameters.set("type", "Processing")
		self.parameters.set("cost", cost) #Cost in dollars per plant
		self.parameters.set("totalCost", size * cost)
		self.parameters.set("labour", labourhours)

	def profit(self):
		cost = self.parameters.get("cost")
		size = self.parameters.get("size")
		return cost * size #A processing event that changes the product towards its final state
class Watering(Processing): #A specific process class for watering since its common to all plants
	def __init__(self, start, object, size):
		super().__init__(start, object, size, -0.02, 0.34)#All plants needs watering with the same cost, so it gets it own class to encapsulate that
		self.type = "Watering"#Keep em wet
