#  Should handle word tokenizing and POS tagging

from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient


class word_pos_tag:

	def __init__(self):
		self.openDBClient()
		self.bootStrapTokenizers()
		self.counter = 0;
	
	def updateDB(self):
		#obj_ids = self.collection.insert([{"sentence" : s, "processed":0} for s in self.sents]) # Code to bulk insert every sentence of corpus...
		#print(str(len(obj_ids)) + ' Sentence Insertions Made')
		
		obj_id = self.tokenCollection.insert({"tokens": self.tokenized, "processed":0})
		#print(obj_id)
		
		self.sentCollection.update({'_id':self.sent['_id']}, { "$set": {'processed':1}})
		self.counter += 1
	
	def tokenizeNextSentence(self):
		self.grabSentence()
		if self.sent:
			#print(self.sent['_id'])
			#print(self.sent['sentence'])
			self.tokenized = self.pos_tag(self.tokenize(self.sent['sentence']))
			#print(self.tokenized)
			self.updateDB()
	
	def grabSentence(self): #should grab the next sentence from the sentence DB
		self.sent = self.sentCollection.find_one({'processed':0})
	
	def bootStrapTokenizers(self):
		self.tokenize = nltk.word_tokenize
		self.pos_tag = nltk.pos_tag
	
	def openDBClient(self):
		self.connection = MongoClient()
		sentDB = self.connection.sentenceDB
		self.sentCollection = sentDB.testSentences
		
		tokenDB = self.connection.tokenDB
		self.tokenCollection = tokenDB.testSentences
	
	def getCount(self):
		print(str(self.counter) + ' objects inserted')

	
	

tokenizer = word_pos_tag() # this is the expensive task - once the tokenizer and POS tagger are loaded into memory, the operation is quite fast...
for i in range(1000):
	tokenizer.tokenizeNextSentence()
tokenizer.getCount()
