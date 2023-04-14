from DBThread import DB

class Greenhouse_DB(DB):
	def __init__(self):
		super().__init__(DB, "pyoa.db")

	def get_books(self):
		sql = "SELECT * FROM BOOK"