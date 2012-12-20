import pymongo
from pymongo import MongoClient



class doc_insert:

	def __init__(self):
		self.openDBClient()
	
	def saveDoc(self):
		obj_id = self.docCollection.insert({"locationOnDisk" : self.location, "origin" : self.origin, "processed":0 }) # Insert the document...
		print(obj_id)
	
	def insertTextFile(self, location):
		self.location = location
		self.origin = "Manual Text Insert"
		self.saveDoc()
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		docDB = self.connection.docDB
		self.docCollection = docDB.testDocs
	

doc_inserter = doc_insert()
doc_inserter.insertTextFile('../../sample_Huckleberry_Finn.txt')