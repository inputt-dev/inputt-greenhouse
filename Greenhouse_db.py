from DBThread import DB
from Globals import Globals

class Greenhouse_DB(DB):
	def __init__(self, *args, **kwargs):
		super().__init__(DB, "plant_calc.db", args[0])
		farm = Globals.get("farm")

		for plant in farm.plants:
			self.add_plant(plant)

	def add_plant(self, plant):
		ret = []
		select = f"SELECT * FROM PLANTS WHERE NAME = '{plant.name}';"
		index = self.addCommand(select)
		result = self.get_result(index)
		#Check if the plant is in the database, if it is update it with the incoming plant
		#If it not, add it in
		if len(result) == 0: 
			exists = False 
		else: 
			exists = True

		if exists:
			data_tuple = (plant.latin, plant.name)
			update = f"UPDATE PLANTS SET LATIN = ? WHERE NAME = ?"
			self.addCommand(update, data_tuple)
		else:
			data_tuple = (plant.name, plant.latin)
			insert = f"INSERT INTO PLANTS (NAME,LATIN) VALUES (?,?)"
			self.addCommand(insert, data_tuple)

	def add_event(self, event):
		


