from parameters import *
from GreenhouseEvent import *
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta

"""
The plant class encasuplates any farm produce that is harvested regularly
Plant specific information is encapsulated in child classes
"""
class plant:  #defines a plant and its attributes
	def __init__(self, name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice):
		parameters = {}
		parameters["type"] = (name, "The type of Plant")
		parameters["rowspacing"] = (rowspacing, "Distance between planting rows(m)")
		parameters["plantspacing"] = (plantspacing, "Distance between plants in a row(m)")
		parameters["growtime"] = (growtime, "Time duration until its ready to harvest(d)")
		parameters["lifespan"] = (lifespan, "How long the plant lives(d)")
		parameters["determinate"] = (determinate, "Determinate(1 or multiple harvests)")
		parameters["harvestincrement"] = (harvestincrement, "time between harvests for indeterminates(d)")
		parameters["yieldrate"] = (yieldrate, "Yield rate(units/planting increment)")
		parameters["sellprice"] = (sellprice,"Selling price($/planting unit)")
		self.parameters = Parameters(parameters)

	def __str__(self):
		ret = "Plant: " + self.parameters.get("type") + "\n"
		ret += "    Growing Area: (" + str(self.parameters.get("rowspacing")) + "," + str(self.parameters.get("plantspacing")) + ")"
		ret += "    Grow Time:" + str(self.parameters.get("growtime")) + "\n"
		ret += "    Life Span:" + str(self.parameters.get("lifespan")) + "\n"
		ret += "    Determinate:" + str(self.parameters.get("determinate")) + "\n"
		ret += "    Time between harvests:" + str(self.parameters.get("harvestincrement")) + "\n"
		ret += "    Yield Rate:" + str(self.parameters.get("yieldrate")) + "\n"
		ret += "    Sell price:" + str(self.parameters.get("sellprice")) + "\n"
		return ret
	def profit(self):
		return self.parameters.get("sellprice") * self.parameters.get("yieldrate")

	def toCSV(self):
		ret = self.parameters.toCSVData()
		return ret

	def toCSVHeader(self):
		ret = self.parameters.toCSVHeader()
		return ret

	def getEvents(self, plantdate, totalplants):
		ret = []
		#Version 1 of add plant event handling,manual to be replaced with above code when ready
		newEvent = Planting(plantdate, self, totalplants)
		ret.append(newEvent)
		lifespan = self.parameters.get("lifespan") #in days how long the plant lives
		growtime = self.parameters.get("growtime") #How many days it grows before being harvested
		harvestincrement = self.parameters.get("harvestincrement") #After its grown, how many days before you can harvest it again, if its indeterminate

		#Now go through the planting event and calculate the harvesting events
		#starting from the plant date calculate when and how much each subsequent harvesting event yields, until the plant dies
		deathdate = plantdate + timedelta(days=lifespan) #On this day, it dies.
		loopdate = plantdate + timedelta(days=growtime) #Start looping at the first harvest date
		while loopdate < deathdate:
			newEvent = Harvesting(loopdate, self, totalplants)
			ret.append(newEvent)
			#increment to the next harvesting date
			loopdate = loopdate + timedelta(harvestincrement)
		#Add a death event for each plant to remove it from the greenhouse
		newEvent = PlantDeath(deathdate, self, totalplants)
		ret.append(newEvent)
		return ret
	def area(self):
		l = self.parameters.get("rowspacing")
		w = self.parameters.get("plantspacing")
		area = l * w
		return area
class IcebergLettuce(plant):
	def __init__(self):
		rowspacing = 0.38
		plantspacing = 0.28 
		growtime = 80
		lifespan = 81
		determinate = True
		yieldrate = 1
		sellprice = 1.89
		harvestincrement = 2 #its not determinate so set its next harvest to after its dead
		name = "IceBerg Lettuce"
		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)

	def getEvents(self, plantdate, totalplants):
		#Lets add a watering schedule
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#Watering: Water lettuce once to twice per week or every 4 days whenever rainfall is inadequate.
		startdate = plantdate #start watering at the begining until 2 days before harvest
		lifespan = self.parameters.get("lifespan")
		enddate = plantdate + timedelta(days = (lifespan - 2)) 
		loopdate = startdate

		while loopdate <= enddate:
			watering = Watering(loopdate, self, totalplants) #7 cents of water per plant, .34 of minute to water it
			ret.append(watering)
			loopdate = loopdate + timedelta(days = 4)

		return ret
class Saskatoons(plant):
	def __init__(self):
		rowspacing = 5.79
		plantspacing = 0.61 #Meters 
		growtime = 1460
		lifespan = 365 * 25 #Lives for 25 years
		determinate = False
		yieldrate = 6.06 #6.06 Kg per plant per year
		sellprice = 14.97 #Based on coop 4.99 for 300 grams retail
		harvestincrement = 365
		name = "Saskatoon Orchard"
		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)

	def getEvents(self, plantdate, totalplants): #Return all the events associated with saskatoon plants, based on the start date
		
		if totalplants <= 1:  #to catch the recursion for replanting dead plants
			return []

		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death

		#After the basics lets add events to show the lifetime list of actions we do to these plants
		#Set the costs of the actions first
		irrigationCost = 200/totalplants * -1
		sprayingFieldCost = -1 #costs $10,000 to spray the field initially for 10000 seedlings
		cultivateCost = 300/totalplants * -2 #negative to show a cost in money
		irrigationInstallCost = 4000/totalplants * -1 #Initial irrigation install
		sprayHerbicideCost = 150/totalplants *-1 #Spraying herbicide over the whole orchard
		sprayInsecticideCost = 150/totalplants *-1 #Insectide, type TBD, Vol/Area
		sprayFungicideCost = 200/totalplants *-1 #type TBD, along with price and V/A
		irrigationCost = 200/totalplants * -1 #Cost to irrigate orchard after install
		pruningCost = 100/totalplants * -1 #Trimming branches
		caseronCost = 400/totalplants * -1
		sprayLabour = 2/60 #Hours per plant to spray it
		cultivateLabour = 3/60
		irrigationInstallLabour = 15/60
		irrigationLabour = 5/60
		pruningLabour = 12/60 #Lets say 12 minutes per bush to prune it
		mowingLabour = 1.5/60 #Guess 1.5 minutes to mow beside each bush, maybe high includes setup time
		#Year 1:
		#	Spraying
		sprayDate = plantdate  - timedelta(days=30) #Spray it before the planting
		spraying = Processing(sprayDate, self, totalplants, sprayingFieldCost, sprayLabour) #10 hours of labour for spraying
		spraying.type = "Inital field clearing spray"
		ret.append(spraying)
		#	cultivate
		cultivateDate = sprayDate + timedelta(days = 1)
		cultivate = Processing(cultivateDate, self, totalplants, cultivateCost, cultivateLabour)
		cultivate.type = "Initial cultivation"
		ret.append(cultivate)
		#	Install irrigation
		irrigationInstallDate = sprayDate + timedelta(days = 2)
		irrigationInstall = Processing(irrigationInstallDate, self, totalplants, irrigationInstallCost, irrigationInstallLabour)
		irrigationInstall.type = "Irrigation Install"
		ret.append(irrigationInstall)
		#	Plant Seedlings
		#Handled by the super classes getEvents function

		#Year 2:
		#	Spray herbicide
		#	mow the grass
		#	2.5% of seedlings die, remove and replace them
		sprayHerbicideDate = plantdate + relativedelta(years = 1)
		sprayHerbicide = Processing(sprayHerbicideDate, self, totalplants, sprayHerbicideCost, sprayLabour)
		sprayHerbicide.type = "Spraying Herbicide"
		ret.append(sprayHerbicide)

		removeDeadPlantsDate = plantdate + relativedelta(years = 1, days = 2)
		deadPlants = round(totalplants * 0.025)
		newEvent = PlantDeath(removeDeadPlantsDate, self, deadPlants)
		newEvent.type = "Removing saskatoons that died over the last year"
		ret.append(newEvent)

		#Now lets add more events to plant more seedlings to replace losses
		rePlantDate = plantdate + relativedelta(years = 1, days = 4)
		replanting = Planting(rePlantDate, self, deadPlants)
		replacements = super().getEvents(rePlantDate, deadPlants)
		for r in replacements:
			r.parameters.set("type", "Replanting losses({})".format(deadPlants))
		ret.append(replanting)
		#Year 3:
		#	Spray Herbicide
		sprayHerbicideDate = plantdate + relativedelta(years = 2, days = 2)
		sprayHerbicide = Processing(sprayHerbicideDate, self, totalplants, sprayHerbicideCost, sprayLabour)
		sprayHerbicide.type = "Spraying Herbicide"
		ret.append(sprayHerbicide)
		#	Spray insecticide
		sprayInsecticideDate = plantdate + relativedelta(years = 2, days = 3)
		sprayInsecticide = Processing(sprayInsecticideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayHerbicide.type = "Spraying Insecticide"
		ret.append(sprayInsecticide)
		#	7.5% seedlings replacement
		rePlantDate = plantdate + relativedelta(years = 2, days = 4)
		deadPlants = round(totalplants * 0.075)
		replanting = Planting(rePlantDate, self, deadPlants)
		replacements = super().getEvents(rePlantDate, deadPlants)
		for r in replacements:
			r.parameters.set("type", "Replanting losses({})".format(deadPlants))
		ret.append(replanting)
		#Now lets add an event to plant more seedlings
		rePlantDate = plantdate + relativedelta(years = 2, days = 5)
		replanting = Planting(rePlantDate, self, deadPlants)
		replanting.type = "Replanting dead saskatoons"
		ret.append(replanting)

		#Year 4:	Spot spray herbicide(about 1/8 of total area)
		sprayHerbicideDate = plantdate + relativedelta(years = 3, days = 2)
		sprayHerbicide = Processing(sprayHerbicideDate, self, totalplants, sprayHerbicideCost, sprayLabour)
		sprayHerbicide.type = "Spot spraying Herbicide"
		ret.append(sprayHerbicide)
		#Year 4:	Inseciticide 
		sprayInsecticideDate = plantdate + relativedelta(years = 3, days = 3)
		sprayInsecticide = Processing(sprayInsecticideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayInsecticide.type = "Spraying Insecticide"
		ret.append(sprayInsecticide)
		#Year 4:	Fungicide
		sprayFungicideDate = plantdate + relativedelta(years = 3, days = 4)
		sprayFungicide = Processing(sprayFungicideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayFungicide.type = "Spraying Fungicide"
		ret.append(sprayFungicide)
		#Year 4:	irrigate
		irrigationDate = sprayDate + timedelta(days = 2)
		irrigation = Processing(irrigationDate, self, totalplants, irrigationCost, irrigationLabour)
		irrigation.type = "Irrigate orchard"
		ret.append(irrigation)
		#Year 4:	In the fall apply caseron and prune
		pruningDate = plantdate + relativedelta(years = 3, months = 4)
		pruning = Processing(pruningDate, self, totalplants, pruningCost, pruningLabour)
		pruning.type = "Fall pruning"
		ret.append(pruning)

		caseronDate = plantdate + relativedelta(years = 3, months = 4)
		caseron = Processing(caseronDate, self, totalplants, caseronCost, sprayLabour)
		caseron.type = "Caseron herbicide application around bushes"
		ret.append(caseron)
		#	Late may apply 46-0-0 and 11-52-0 blend fertilizer and Late June
		#	mow
		mowingCost = 200/totalplants * -1
		mowingDate = plantdate + relativedelta(years = 3, months = 4, days = 2)
		mowing = Processing(mowingDate, self, totalplants, mowingCost, mowingLabour)
		mowing.type = "Mowing grass between orchard rows"
		ret.append(mowing)
		#	harvest
		#Year 5:
		#Year 5: Spot Spray herbicide(1/8)
		sprayHerbicideCost = 150/totalplants *-1/8
		sprayHerbicideDate = plantdate + relativedelta(years = 4, days = 2)
		sprayHerbicide = Processing(sprayHerbicideDate, self, totalplants, sprayHerbicideCost, sprayLabour)
		sprayHerbicide.type = "Year 5 Spot spraying Herbicide"
		ret.append(sprayHerbicide)
		#Year 5:	Inseciticide 
		sprayInsecticideCost = 150/totalplants *-1
		sprayInsecticideDate = plantdate + relativedelta(years = 4, days = 3)
		sprayInsecticide = Processing(sprayInsecticideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayInsecticide.type = "Year 5: Spraying Insecticide"
		ret.append(sprayInsecticide)
		#Year 5:	Fungicide
		sprayFungicideCost = 200/totalplants *-1
		sprayFungicideDate = plantdate + relativedelta(years = 4, days = 4)
		sprayFungicide = Processing(sprayFungicideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayFungicide.type = "Year 5: Spraying Fungicide"
		ret.append(sprayFungicide)
		#Year 5: mow
		mowingCost = 200/totalplants * -1
		mowingDate = plantdate + relativedelta(years = 4, months = 4, days = 2)
		mowing = Processing(mowingDate, self, totalplants, mowingCost, mowingLabour)
		mowing.type = "Year 5: Mowing grass between orchard rows"
		ret.append(mowing)
		#	harvest	
		#Year 6:
		#	spot spray herbicide
		spotSprayHerbicideCost = 150/totalplants *-1/8
		spotSprayHerbicideDate = plantdate + relativedelta(years = 5, days = 2)
		spotSprayHerbicide = Processing(sprayHerbicideDate, self, totalplants, spotSprayHerbicideCost, sprayLabour)
		spotSprayHerbicide.type = "Year 6 Spot spraying Herbicide"
		ret.append(spotSprayHerbicide)
		#Year 6:	spray insecticide and fungicide
		sprayFungicideDate = plantdate + relativedelta(years = 5, days = 4)
		sprayFungicide = Processing(sprayFungicideDate, self, totalplants, sprayFungicideCost, sprayLabour)
		sprayFungicide.type = "Year 6: Spraying Fungicide"
		ret.append(sprayFungicide)
		sprayInsecticideDate = plantdate + relativedelta(years = 5, days = 3)
		sprayInsecticide = Processing(sprayInsecticideDate, self, totalplants, sprayInsecticideCost, sprayLabour)
		sprayInsecticide.type = "Year 6: Spraying Insecticide"
		ret.append(sprayInsecticide)
		#Year 6:	irrigate

		irrigationDate = plantdate + relativedelta(years = 5, days = 2)
		irrigation = Processing(irrigationDate, self, totalplants, irrigationCost, irrigationLabour)
		irrigation.type = "Irrigate orchard"
		ret.append(irrigation)
		#Year 6: mow
		#	harvest
		#	apply caseron
		#	prune
		#	fertilizer may and june
		#Year 7:
		#	Spot Spray herbicide(1/8)
		#	Insecticide
		#	Fungicide
		#	mow
		#	harvest	
		#Year 8:
		#	spot spray herbicide
		#	spray insecticide and fungicide
		#	irrigate
		#	mow
		#	harvest
		#	apply caseron
		#	prune
		#	fertilizer may and june
		#Year 9:
		#	Spot Spray herbicide(1/8)
		#	Insecticide
		#	Fungicide
		#	mow
		#	harvest		
		#Year 10:
		#	spot spray herbicide
		#	spray insecticide and fungicide
		#	irrigate
		#	mow
		#	harvest
		#	apply caseron
		#	prune
		#	fertilizer may and june
		#	
		#Cooling, put into refigerated truck or quickly transporting it to the commercial fridge


		#Sorting, on a conveyor belt for workers to remove unripe berries

		#Freezing, storing the berries for transport either in a bulk box with the berries frozen together or frozen individually
		#and poured into other containers(plastic bags)

		#Canning, 

		#Juicing

		#Baking into pies

		#Harvesting happens over a month, so set the duration of Harvest events to 30 days
		#Set the planting labour per plant to 10 minutes, as well as dead plant removal
		for event in ret:
			if type(event) == Harvesting:
				event.parameters.set("duration", 30)
				event.parameters.set("labour",  20/60)
			if type(event) == Planting:
				event.parameters.set("duration", 14)
				event.parameters.set("labour",  8/60)
			if type(event) == PlantDeath:
				event.parameters.set("duration", 1)
				event.parameters.set("labour",  10/60)
		return ret

class IndeterminateTomatoes(plant):
	def __init__(self):
		rowspacing = 0.37
		plantspacing = 0.79 #Meters apart(12-18 inches)
		growtime = 65
		lifespan = 180
		determinate = False
		yieldrate = 12
		sellprice = 5.5
		harvestincrement = 17
		name="Indeterminate Tomatoe"

		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 

class LongEnglishCucumbers(plant):
	def __init__(self):
		rowspacing = 0.9
		plantspacing = 0.23 #Meters apart(12-18 inches)
		growtime = 85
		lifespan = 365
		determinate = False
		yieldrate = 12
		sellprice = 2.49
		harvestincrement = 21
		name="Long English Cucumbers"

		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 

class CanaryBellPeppers(plant):
	def __init__(self):
		rowspacing = 0.53
		plantspacing = 0.38 #Meters apart(12-18 inches)
		growtime = 85
		lifespan = 86
		determinate = True
		yieldrate = 7.5
		sellprice = 2.1
		harvestincrement = 2 #its not determinate so set its next harvest to after its dead
		name = "Canary Bell Peppers"

		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 

class CaliforniaWonderGreenBellPeppers(plant):
	def __init__(self):
		rowspacing = 0.37
		plantspacing = 0.53 #Meters apart(12-18 inches)
		growtime = 80
		lifespan = 81
		determinate = True
		yieldrate = 9
		sellprice = 1.53
		harvestincrement = 2 #its not determinate so set its next harvest to after its dead
		name = "California Wonder Green Bell Peppers"

		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 
class TomatoesOV(plant):
	def __init__(self):
		rowspacing = 0.37
		plantspacing = 0.53 #Meters apart(12-18 inches)
		growtime = 80
		lifespan = 81
		determinate = True
		yieldrate = 9
		sellprice = 1.53
		harvestincrement = 2 #its not determinate so set its next harvest to after its dead
		name = "Tomatoes on the Vine"
		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 
class NankingCherry(plant):
	def __init__(self):
		rowspacing = 0.37
		plantspacing = 0.53 #Meters apart(12-18 inches)
		growtime = 80
		lifespan = 365 * 35
		determinate = False
		yieldrate = 9
		sellprice = 1.53
		harvestincrement = 365 #its not determinate so set its next harvest to after its dead
		name = "Nanking Cherries"
		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)

class TomatosMountainMagic(plant):
	def __init__(self):
		rowspacing = 0.53
		plantspacing = 0.38 #Meters apart(12-18 inches)
		growtime = 85
		lifespan = 86
		determinate = True
		yieldrate = 7.5
		sellprice = 2.1
		harvestincrement = 2 #its not determinate so set its next harvest to after its dead
		name = "Tomatos: Mountain Magic"

		super().__init__(name, rowspacing, plantspacing, growtime, lifespan, determinate, harvestincrement, yieldrate, sellprice)
	def getEvents(self, plantdate, totalplants):
		ret = super().getEvents(plantdate, totalplants) #a list of all the events related to basic plant harvesting, and death
		#step 1: Germinate the seeds
		return ret 

"""Germinate

Use seed starting mix, such as Miracle Gro or Jiffy Mix, to start your seeds. Fill a bowl with some mix and knead in some water till the
mix is saturated but not soggy.
I use egg cartons to start my seeds in. You can use either the clear plastic or Styrofoam cartons; do NOT use the paper ones. Fill the
trays with seed mix and firm the mix down into the cells.
If you are growing multiple varieties, you will need a labeling system to keep track of what tray contains what variety. Use tape, plant
tags, etc to mark the trays. Be creative - do whatever works best for you to keep track of the varieties.
Plant the seeds about 1/4 inch deep, 2 seeds per cell. I use a pencil with the tip broken off to make a 1/4" deep hole in the center of
each cell, and I drop 2 seeds into each hole and firm the mix around the seeds to completely cover them.

Keep your trays moist and warm to speed germination. Loosely fit plastic wrap over the tops of the trays, to keep water in but still allow for air circulation. Light is not required to germinate seeds.

In anywhere from 3 to 15 days, you should start to see tiny seedlings emerge.

When your seedlings are up and the first 2 leaves (cotyledon leaves) start to open, you will need to put your seedlings under a light.

Use a cheap fluorescent shop light for your seedlings. I use 4' fixtures that take 2 bulbs each. You can use regular fluorescent tubes, or ones specially made for plants. I use GE "Plant & Aquarium" tubes in my fixtures.

It's very important to keep your seedlings within 4" of the lights, preferably closer. If you keep the light too far from the seedlings, they will get very "leggy" - tall and skinny - and might collapse.

Keep the seed starting mix moist but not soggy, and water whenever the surface becomes dry to the touch (but NOT completely dry).
Keep the seedlings watered - not overwatered, but don't let them get so dry they wilt, either.

Make sure they are kept within 4" of the grow light(s). You can adjust the chain that the light hangs from, or you can put the seedling trays on books or boxes to adjust their distance from the light.

Make sure your grow light setup is in a room where it won't get too hot (80+ deg F) or too cold (below 50 deg F).

You will want the seedlings to be easily accessible, because you will be watering them often (every couple days).

Monitor your seedlings and make sure they are growing well. The cotyledon leaves should grow up to 1 inch wide each, and should be a healthy green color.

Damping off can be a problem - this is a disease that causes young plants to collapse at the soil line and die. If any of your seedlings damp off, remove the infected plants and the mix they grew in to prevent spreading the disease to other plants.

Potting up:
When your tomato seedlings are showing their first set of true leaves, it's time to put them in individual pots.

I use 16-ounce disposable plastic cups. These work well and are cheap.

Fill the cups with Miracle Gro Potting Mix or similar potting mix. I use Miracle Gro because it eliminates the need to apply fertilizer manually.

Use a pencil to make a hole in the center of the mix in each cup. The hole should be about 1 inch wide and 3-4 inches deep.

Choose the best seedlings to pot up, and discard the rest. If you pot up more than you can grow in your garden, just give away the extra plants when they are bigger.

Carefully loosen the seed starting mix around your chosen seedlings. Gently scoop out each seedling, being careful not to damage the roots or stem. Tap off excess mix from the roots so they will fit easily into the hole you made in the mix in the larger cups. Do this one at a time, and when a seedling has been uprooted, put it in the larger cup immediately.

Firm the potting mix around the roots and the stem of each seedling. Bury the stem all the way up to the cotyledon leaves - roots will grow from the stem and benefit the plant.

Label your cups with the variety name of each plant. I write on the side of the cup with a Sharpie.

Thoroughly water all the cups. Make sure you don't splash potting mix all over the seedlings when you water them.

When the seedlings are all potted up, put them under the grow light(s) and keep them within 4-5 inches of the lights.

Planting Out:
When the danger of frost has passed, it's time to get the plants out in the garden. Your garden should be tilled ahead of time, and adding compost is good. Soil pH should be from 6 to 7 (slightly acidic to neutral) for tomatoes.

Dig a trench about 1 foot long, with one end deeper than the other. Carefully remove the plant from its pot and loosen the root ball. Place the root ball in the deeper end of the trench, and lay the seedling on its side with the stem in the trough.

Remove all the leaves from the part of the stem that is in the trench, and leave the top few leaves on where they will be above the ground. Bury the roots and bare stem in the trench, leaving only the top few leaves sticking out. Don't worry about their being sideways - the plant will correct itself and grow upwards within a few days.

Trenching plants allows roots to develop along the entire buried portion of the stem. They say this increases yields - I haven't done any tests of my own but it makes sense. More roots allow for more nutrients to be absorbed.

Repeat the trenching process to all your plants, keeping them spaced at least 2 feet apart (if you plan on pruning) or 3-4 feet apart (if you won't be pruning).

When all the plants are trenched, water them thoroughly and add mulch if desired. Drive stakes or cages into the ground, making sure you don't puncture the buried stem.

Caring and pruning:
Your tomato growing spot should receive at least 6 hours of sun a day for good yields. I only get at most 5 hours a day, but my plants sill produce fairly well.

Keep the plants watered, but not overwatered. Don't let them dry out or inconsistently water them. Not enough water can cause fruit problems like Blossom End Rot, and overwatering can cause the fruit to crack.

To prune your plants, pinch off the suckers (shoots that come out from between each leaf and the main stem). You can let a few suckers grow for more fruit per plant, but as a general rule, the more fruit you allow, the smaller they will be. Last year I let one sucker grow on each plant for a total of 2 stems per plant. The rest of the suckers were pinched off as they grew.

If you prune your plants, tie the stems to a stake. If you don't prune them, you can let them sprawl on the ground or place tomato cages around the plants.

Harvesting:
You should start getting ripe fruit anywhere from 2 to 4 months after planting out in the garden. Different varieties have different DTM (days to maturity), so some will ripen 70 days after transplanting and some will ripen late, 100 days or more. Usually when you purchase seed, the description will tell you the DTM.

You can cut or twist the fruit off when it is fully colored. Some heirloom varieties ripen green or have green shoulders when ripe; Google the varieties you are growing to see what they look like when ripe.

From this point forward, it's mostly watering and picking fruit till the season ends.

Here are a couple useful links to help with any problems the tomatoes may have:

"""

