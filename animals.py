"""
Animals on the ranch!
"""
class animal:
	#manipulate, store, extract, indentify,
	totalCount = 0
	def __init__(self): #a list of the variables, the init function will add them to the variables variable
		#{type: sheep
		# QR Code: Fully identifies and shows parentage
		# name: customized name
		# Primary: A primary key to uniquely and efficiently single out any individual member
		# Mother: primary key of Mom
		# Father: primary key of Dad
		totalCount = 0

		if variables is None: #Set the default
			variables = {"type": ("Basic animal", "Animal species"),
						"QRCode": (None, "QR code identifying this specific animal"),
						"Name": ("MeatBag", "Probably shouldnt name the ranch animals"),
						"Primary": (animal.totalCount, "Primary key"),
						"Mother": (None, "Primary key of the mother"),
						"Father": (None, "Primary key of the father"),
						"Children": ([], "A list of its children and their primary keys"),
						"Alive": (True, "Alive on the ranch")}
		self.parameters = Parameters(variables) #Initialize the object
		animal.totalCount += 1 #The primary key is the animal count
	def getVariable(self, name): #a String like
		return variables.getVariable(name)
	def mate(self, partner):
		child = animal() #The baby is born!
		child.setParent(self.getPrimary(), partner.getPrimary()) #set the parent information for the new animal
		partner.variables.addTo("Children", child) #Add the information to the parents as well
		self.parameters.addTo("Children", child)
	def setParent(self, mother, father):
		self.parameters.set("Mother", mother)
		self.parameters.set("Father", father)
class sheep(animal):
	def __init__(self):
		super().__init__()
		self.parameters.set("type", "Sheep") #Change the basic animal to a sheep

