from DBThread import DB

class Greenhouse_DB(DB):
	def __init__(self, *args, **kwargs):
		super().__init__(DB, "plant_calc.db", args[0])
		