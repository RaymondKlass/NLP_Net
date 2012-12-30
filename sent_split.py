from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient



class sent_split:

	def __init__(self):
		self.openDBClient()
		self.bootstrapSentSplitter()
	
	def saveSents(self):
		obj_ids = self.sentCollection.insert([{"sentence" : s, "processed":0, "document_id":self.document['_id']} for s in self.sents]) # Code to bulk insert every sentence of corpus...
		print(str(len(obj_ids)) + ' Sentence Insertions Made')
	
		#easier and faster to just insert an array of the object IDs back into the original document...
		self.docCollection.update({'_id':self.document['_id']}, { "$set": {'sents':obj_ids, 'processed':1}}) #### -- Check this line - then also start work on the document entry module...
	
	
	
	def splitText(self, text):
		# this is where you would dynamically pull the text from the repository...  Maybe use amazon S3 for text...
		self.document = self.docCollection.find_one({"processed":0})
		if self.document != None:
			f = open(self.document['locationOnDisk'])
			raw = f.read()
			self.sents = self.sent_tokenizer.tokenize(raw)
			self.saveSents()
	
	
	def bootstrapSentSplitter(self):
		self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		sentDB = self.connection.sentDB
		self.sentCollection = sentDB.testSents
		
		docDB = self.connection.docDB
		self.docCollection = docDB.testDocs
	

splitter = sent_split()
splitter.splitText('../sample_Huckleberry_Finn.txt')