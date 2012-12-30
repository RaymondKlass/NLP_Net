from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient


class relation_extractor:

	def __init__(self):
		self.openDBClient()
		self.bootstrapAdditionalClasses()

			
	def processNextTokens(self):
		self.loadTokens()		
		print(self.tokens)
		self.relationBounds = self.relationIdentify.returnRelationshipBounds(self.tokens['tokens'])
		self.nounPairIdentifier.returnNounPairsExtracted(self.relationBounds, self.tokens['tokens'])
		# -- remove lie below after initial testing...
		self.tokenCollection.update({'_id':self.tokens['_id']}, { "$set": {'processed':1}}) #### -- Check this line - then also start work on the document entry module...
			
	def loadTokens(self):
		self.tokens = self.tokenCollection.find_one({"processed":0})
	
	
	def bootstrapAdditionalClasses(self):
		self.relationIdentify = relation_identifier()
		self.nounPairIdentifier = noun_pair_identifier()
	
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		tokenDB = self.connection.tokenDB
		self.tokenCollection = tokenDB.testTokens
		
		relationDB = self.connection.relationDB
		self.relationCollection = relationDB.testRelations
		
		relationGroupDB = self.connection.relationGroupDB
		self.relationGroupCollection = relationGroupDB.testRelationGroups
		
		wordDB = self.connection.wordDB
		self.wordCollection = wordDB.testWords

		
		
###############################################################################################################		
###############################################################################################################		
###############################################################################################################		

###  <!-- Should be initially finished...

class relation_identifier: 
	
	def __init__(self):
		self.bootstrapSLists()
	
	def returnRelationshipBounds(self, tokens):
		self.ePoints = [] # initialize a new array to hold the bounds of the sentence passed in...
		for i, word in enumerate(tokens):
			if i == len(tokens)-1:
				continue
			if word[1] in self.catV:
				self.ePoints.append([i, i+1])
				if tokens[i+1][1] in self.catP:
					self.ePoints.append([i, i+2])
				elif tokens[i+1][1] in self.catW:
					self.handleWP(tokens, i+1)
		return self.collapsePairs()	
		
	def collapsePairs(self): #ePoints is now available as a class variable, and no longer needs to be passed
		ends = []
		for e in self.ePoints:
			if len(ends) == 0:
				ends.append(e)
				continue
			if e[0] <= ends[len(ends)-1][1]:
				ends[len(ends)-1][1] = e[1]
			else:
				ends.append(e)
		return ends
	
	def handleWP(self, tokens, p):
		for i, word in enumerate(tokens[p:]):
			if i == len(tokens):
				return None
				if word[i] in catP:
					self.ePoints.append([p,i+1])
		return False	
		
		
	def bootstrapSLists(self):
		#### <!-- Basic Grammer:
		# V | VP | VW*P
		# Based on U of Washington's Reverb Relation Extractor --> ####
	
		self.catV = ['RB', 'RBS', 'RP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'WRB', 'VBZ']
		self.catW = ['DT', 'JJ', 'JJR' 'JJS', 'NN', 'NNP', 'NNPS', 'PDT', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'WDT', 'WP', 'WP$', 'WRB']
		self.catP = ['IN', 'RP', 'TO']	


###############################################################################################################		
###############################################################################################################		
###############################################################################################################


class noun_pair_identifier:

	def __init__(self):
		self.bootstrapSLists()


	def findPrevNP(self, i): 
		if self.ends[i][0] == 0: # if the current relationship is the first word of the sentence...
			return None
		
		# determine the left boundary of the area
		left = 0
		if i > 0:
			left = self.ends[i-1][1]
		
		right = self.ends[i][0]
		
		NPs = [] #array to hold the found Noun Pairs...
		for word in self.s[left:right]:
			if word[1] in self.catNP:
				NPs.append(word[0])
		if len(NPs) == 0:
			if i > 0:
				return self.findPrevNP(i-1)
			else:
				return None
		return NPs
	
	## !-- Finds the next appropriate Noun-Pairs... Afte the relationship given...	
	def findNextNP(self, i):
		if self.ends[i][1] == len(self.s)-1: #if the relationship stretches all the way to the end of the sentence
			return None
		
		left = self.ends[i][1]
		
		right = len(self.s)-1 #initialize the right boundary to last letter of the sentence...
		if i < len(self.ends)-1: # means that this is not the last relationship of the sentence...
			right = self.ends[i+1][0]
		
		NPs = []
		for word in self.s[left:right]:
			if word[1] in self.catNP:
				NPs.append(word[0])
		if len(NPs) == 0:
			if i < len(self.ends)-1:
				return self.findNextNP(i+1)
			else:
				return None
		return NPs
		

	def extractNPFromRelation(self, i):
		NPs = []
		for word in self.s[self.ends[i][0]:self.ends[i][1]]:
			if word[1] in self.catNP:
				NPs.append(word)
		if len(NPs):
			return NPs
		return None

	
	def returnNounPairsExtracted(self, ends, s): ## Call this function... - the s referred to here should be an array of tokens
		self.ends = ends
		self.s = s
		
		relations = [];
		
		for i, e in enumerate(ends):
			r = {}
			r['prevNP'] = self.findPrevNP(i)
			r['nextNP'] = self.findNextNP(i)
			r['addNP'] = self.extractNPFromRelation(i)
			r['relation'] = self.s[self.ends[i][0]:self.ends[i][1]]
			if r['prevNP'] and r['nextNP'] and r['relation']:
				relations.append(r)
	
		for r in relations:
			print('prev: ' +str(r['prevNP']) + ' -> next: ' +str(r['nextNP']) + ' additional: ' +str(r['addNP']))

	
	def bootstrapSLists(self):
		self.catNP = ['NN', 'NNS', 'NNP', 'NNPS', 'PRP', '$PRP']


###############################################################################################################		
###############################################################################################################		
###############################################################################################################


relationExtract = relation_extractor()
relationExtract.processNextTokens()








