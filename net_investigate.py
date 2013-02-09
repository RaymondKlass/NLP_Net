from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient
import operator

class net_investigate:

	def __init__(self):
		self.openDBClient()
		self.word = []
		self.wordCache = {}

	
	def investigateWordPair(self, word1, word2):
		self.seedWord(word1)
		self.seedWord(word2)
		
		self.wordPos = {}
		self.discoverAllPaths(minScore = .000015, cScore = 1, cPath = [self.word[0]['word']], target = self.word[1]['word'])
		
		sorted_x = sorted(self.wordPos.iteritems(), key=operator.itemgetter(1), reverse=True)

		for item in sorted_x:
			print item[0] +' ' + str(item[1])

	
	
	#def loadWord(self, word): 
	#	if word in self.wordCache:
	#		return self.wordCache[word]
	#	else:
	#		if len(self.wordCache) >= 100000:
	#			del self.wordCache[self.wordCache.keys()[0]]
	#		
	#		self.wordCache[word] = self.wordCollection.find_one({'word':word})
	#		return self.wordCache[word]
	
	def loadWord2(self, word): # utilize mongoDB's caching instead...
		return self.wordCollection.find_one({'word':word})
	
	
	def discoverAllPaths(self, minScore ,cScore, cPath, target): ######  This function needs serious help...
		
		if cScore < minScore:
			return False
		
		currentWord = self.loadWord2(cPath[-1])
		
		if not currentWord:
			return False
		for link in currentWord['link']:

			if link == target: #means a path has been found...
				for node in cPath:
					if node in self.wordPos:
						self.wordPos[node] = self.wordPos[node] + cScore 
					else:
						self.wordPos[node] = cScore
						
				return False # return after finding a valid link - but continue to look for others that can be of valid length that connect through the parent node

			else:
				if link not in cPath: #indicates that this is a path that has not been taken yet...
					try: # Need to try here because sometimes a word will not have a link
						newList = cPath[:]
						newList.append(link)
						self.discoverAllPaths( minScore, cScore * (currentWord['link'][link]/sum(currentWord['link'].values())), newList , target)
					except:
						return False
			
			
	
	def investigateSingleWord(self, iWord):
		self.seedWord(iWord)
		self.sortWordUsage(self.word[0])
	
	def sortWordUsage(self, word):
		sorted_x = sorted(word['link'].iteritems(), key=operator.itemgetter(1), reverse=True)
		print(sorted_x.keys())
	
	def seedWord(self, iWord):
		self.word.append(self.wordCollection.find_one({'word':iWord.lower()}))
	
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		wordDB = self.connection.wordDB
		self.wordCollection = wordDB.testWords
		
nI = net_investigate()
#nI.testListCall()
nI.investigateWordPair('arm', 'tree')