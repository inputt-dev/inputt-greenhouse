from DBThread import DB

class Greenhouse_DB(DB):
	def __init__(self):
		super().__init__(DB, "plant_calc.db")
