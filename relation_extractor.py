from __future__ import division
import nltk, re, pprint
import pymongo
from pymongo import MongoClient


class relation_extractor:

	def __init__(self, isAnalyticsOn = False):
		self.openDBClient()
		self.bootstrapAdditionalClasses()
		self.isAnalyticsOn = isAnalyticsOn; # turn the analytics off by defualt
	
	def turnAnalyticsOn(self): # turn anaylics mode on
		self.isAnalyticsOn = True;
		
	def turnAnalyticsOff(self): # turn analytics mode off
		self.isAnalyticsOn = False;
	
	def insertRelations(self):
		
		for r in self.relations:
			for g in [{'words':[a,b], 'sent_id':self.tokens['sent_id'], 'document_id' : self.tokens['document_id'], 'relation':r['relation'][0][0]} for a in r['prevNP'] for b in r['nextNP']]:
				obj_id = self.relationCollection.insert(g)
				
				#nObject_id = self.relationGroupCollection.update({'words':{'$in':[[g['words'][0], g['words'][1]], [g['words'][1], g['words'][0]]]}}, 
				#{'$push':{'relation_id':obj_id }, '$set':{'words':g['words']}}, True)# alternate way to do this...
				
				self.relationGroupCollection.update({'words':[g['words'][0], g['words'][1]], 'words':[g['words'][1], g['words'][0]]}, {'$push':{'relation_id':obj_id }}, True) # update or insert
				self.wordCollection.update({'word':g['words'][0]}, {'$inc':{'link.'+g['words'][1]+"'": 1 }}, True)
				
				if self.isAnalyticsOn: # links to a simple analytics mode. 
					print(self.wordCollection.update({'word':g['words'][1]}, {'$inc':{'link.'+g['words'][0]+"'": 1 }}, True))
					
					obj = self.relationGroupCollection.find_one({'words':[g['words'][0], g['words'][1]]})
					print(obj)
					print(self.wordCollection.find_one({'word':g['words'][0]}))
					print(self.wordCollection.find_one({'word':g['words'][1]}))
				
				
			
	def processNextTokens(self):
		self.loadTokens()		
		#print(self.tokens)
		relationBounds = self.relationIdentify.returnRelationshipBounds(self.tokens['tokens'])
		self.relations = self.nounPairIdentifier.returnNounPairsExtracted(relationBounds, self.tokens['tokens'])
		# -- remove lie below after initial testing...
		self.insertRelations()
		self.tokenCollection.update({'_id':self.tokens['_id']}, { "$set": {'processed':1}}) #### -- Check this line - then also start work on the document entry module...
			
	def loadTokens(self):
		self.tokens = self.tokenCollection.find_one({"processed":0})
	
	
	def bootstrapAdditionalClasses(self):
		self.relationIdentify = relation_identifier()
		self.nounPairIdentifier = noun_pair_identifier()
	
	
	def openDBClient(self):
		self.connection = MongoClient()
		
		docDB = self.connection.docDB
		self.docCollection = docDB.testDocs
		
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
	
		return relations

	
	def bootstrapSLists(self):
		self.catNP = ['NN', 'NNS', 'NNP', 'NNPS', 'PRP', '$PRP']


###############################################################################################################		
###############################################################################################################		
###############################################################################################################


relationExtract = relation_extractor(True)
for i in range(1):
	relationExtract.processNextTokens()
print('done')







