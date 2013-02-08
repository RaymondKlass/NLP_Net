from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient
import operator

class net_investigate:

	def __init__(self):
		self.openDBClient()
		self.word = []

	
	def investigateWordPair(self, word1, word2):
		self.seedWord(word1)
		self.seedWord(word2)
		
		self.paths = []
		self.discoverAllPaths(minScore = .2, cScore = 1, cPath = [self.word[0]], target = self.word[1])
		#print(self.paths)
	
	
	def loadWord(self, word):
		self.seedWord(word)
		print(self.word[-1])
	
	
	def discoverAllPaths(self, minScore ,cScore, cPath, target):
		print(cPath)
		#print(target)
		
		if cScore < minScore: #if the min Score ofthe path ever becomes less than the min required - kill that path
			return false
		
		
		
		for link in cPath[-1]['link']:
			# load a dynamic cache with the word objects - check if the word has been previously navigated to in this path - follow if not - loading from cache if possible - otherwise pull from DB...
			word = self.loadWord(link)
			print word
			#if(link)
			
	
	def investigateSingleWord(self, iWord):
		self.seedWord(iWord)
		self.sortWordUsage(self.word[0])
	
	def sortWordUsage(self, word):
		sorted_x = sorted(word['link'].iteritems(), key=operator.itemgetter(1), reverse=True)
		print(sorted_x)
	
	def seedWord(self, iWord):
		self.word.append(self.wordCollection.find_one({'word':iWord.lower()}))
	
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		wordDB = self.connection.wordDB
		self.wordCollection = wordDB.testWords
		
nI = net_investigate()
nI.investigateWordPair('house', 'grass')