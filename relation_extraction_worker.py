from __future__ import division
import nltk, re, pprint
from nltk.corpus import conll2000
from nltk.chunk.util import conlltags2tree
import boto.dynamodb
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import uuid


class nltkHelper():

	def __init__(self,debug = False):
		self.location = None
		self.bootstrapS3()
		self.bootstrapSentSplitter()
		self.bootstrapTokenizer()
		self.bootstrapRelationshipExtractor()
		self.bootstrapChunkTagger()
		self.bootstrapNounPhraseAssembler()
		self.bootstrapRelationInserter()
		self.debug = debug
		self.output = {} # build a dynamic output var - to include debug info if that mode is True

		
		
	def bootstrapS3(self):
		self.s3Conn = S3Connection('S3_KEY_ID', 'S3_SECRET_KEY')	
		self.bucket = self.s3Conn.get_bucket('S3_BUCKET')
		
	
	def bootstrapRelationInserter(self):
		self.dynamoConn = boto.dynamodb.connect_to_region(
						'us-east-1',
						aws_access_key_id = 'DYNAMODB_KEY_ID',
						aws_secret_access_key = 'DYNAMODB_SECRET_KEY')
		
		word_table_left_schema = self.dynamoConn.create_schema(
						hash_key_name = 'id_word',
						hash_key_proto_value = str,
						range_key_name = 'target_word',
						range_key_proto_value = str)
		self.word_table_left = self.dynamoConn.table_from_schema(name="nlp_word_left", schema=word_table_left_schema)
						
		word_table_right_schema = self.dynamoConn.create_schema(
						hash_key_name = 'id_word',
						hash_key_proto_value = str,
						range_key_name = 'target_word',
						range_key_proto_value = str)
		self.word_table_right = self.dynamoConn.table_from_schema(name="nlp_word_right", schema=word_table_right_schema) 
	
	
	def insertRelations(self, relations):
		# Method to handle the data insertion
		# schema: sentence:
		#		  relations: [left, right, relation],[]

		
		for r in relations['relations']:
		
			leftNP = r[0]
			rightNP = r[1]
			relation = r[2]		
			
			allLeftNouns = [] # a blank var to hold all of the Left Nouns
			allRightNouns = [] # a blank var to hold all of the Right Nouns
			
			for eL in leftNP:
				
				if eL[1] in ['NN', 'NNS', 'NNP', 'NNPS']: # only supporting word - word relations for nouns...
					allLeftNouns.append(eL[0].lower())
					
					for eR in rightNP:
						if eR[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
							allRightNouns.append(eR[0].lower())
							
							# Time to begin making the insertions into the word - word relationship table
							
							# First place the left to right connection - then afterwards create the back link
							# which will enable faster database traversal
							try:
								item = self.word_table_left.new_item(hash_key = eL[0].lower(), range_key = eR[0].lower())
								item.add_attribute('count',1)
								item.save()
							except:
								pass
							
							# now add the right to left links which can be used to process a non-directed neural net...
							
							try:
								item = self.word_table_right.new_item(hash_key = eR[0].lower(), range_key = eL[0].lower())
								item.add_attribute('count',1)
								item.save()
							except:
								pass				
	
	
	
	def bootstrapNounPhraseAssembler(self):
		self.NPAssembler = assembleNounPhrases()	
	
	
	def bootstrapChunkTagger(self):
		train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
		self.NPChunker = ChunkParser(train_sents)
	
	def bootstrapSentSplitter(self):
		self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	
	
	def bootstrapTokenizer(self):
		self.tokenize = nltk.word_tokenize
		self.pos_tag = nltk.pos_tag
	
	def bootstrapRelationshipExtractor(self):
		self.relationIdentify = relation_identifier2()
	
	def insertRaw(self, location): # this is the main function to insert new text into the system...
		self.location = location
		
		k = Key(self.bucket)
		k.key = location

		self.raw = k.get_contents_as_string() # these already split files should be small enough to store in the RAM of the computer - so this should be safe
											  # If I begin dealing with significantly larger files - then stream text instead

		self.sents = self.sent_tokenizer.tokenize(self.raw)
		
		for sent in self.sents:
		
			sentReturn = {} # var to hold the output of one sentence worth of input
			
			tokenized = self.pos_tag(self.tokenize(sent))

			NPs = self.NPChunker.parse(tokenized)
			
			relationBounds = (self.relationIdentify.returnRelationshipBounds(tokenized))
			
			sentReturn['relations'] = self.NPAssembler.returnRelationships(tokenized, relationBounds, NPs)
			sentReturn['sentence'] = sent
		
			self.insertRelations(sentReturn)

		return True



########################
# Class that deals with the identifying of relatioinships


class relation_identifier2():
	def __init__(self):
		self.bootstrapSLists()
	
	def bootstrapSLists(self):
		
		# Verb definition -  (v1)? + (v2) + (v3)?
		
		self.v1 = ['RB']
		self.v2 = ['MD', 'VB', 'VBD', 'VBP', 'VBZ', 'VBG', 'VBN']
		self.v3 = ['RP', 'RB']
		
		# Word definition - (w1)
		
		self.w1 = ['PRP$', 'CD', 'DT', 'JJ', 'JJS', 'JJR', 'NN', 'NNS', 'NNP', 'NNPS', 'POS', 'RB', 'RBR', 'RBS', 'VBN', 'VBG'] # PRP removed as per UW syntactical constraint
		
		# Preposition Definition - (p1)? + (p2) + (p3)?
		
		self.p1 = ['RB']
		self.p2 = ['IN', 'TO', 'RP']
		self.p3 = ['RB']
		
		# stop tag list
		
		self.stopTags = ['CC', 'PRP']
		
		# stop word list
		
		self.stopWords = [',', 'that', 'if', 'because']
		
		
	
	########################
	# Patterns to recognize - U of W
	#
	# Short: VP?
	# Long: V(W*P)?
	
	def returnRelationshipBounds(self, tokens): #input should be a POS tagged, single sentence
		self.ePoints = []
		for i, word in enumerate(tokens): # the word elements are tuples (word, POS) - we will only use the POS
			if i == len(tokens)-1 or i == 0: # if this is the last token - then it cannot be a relational phrase
				continue
			
			#first look for a word in the required v2
			if word[1] in self.v2: # means we've found a possible relationship...
				start = 0
				# this cannot be the first word of the sentence - so simply check the previous word to see if it is in v1, include it if so...
				if tokens[i-1][1] in self.v1:
					start = i-1 #i-1 would be the start of the relational phrase 
				else:
					start = i # this is the case when we did not match v1
				
				self.ePoints.append([start,i]) # it could be longer - but this is at least a valid relationship as just a single verb...
				
				end = self.findEnd(tokens, start)
				if end:
					self.ePoints.append([start, end])
		
		return self.collapseRelations(tokens) 
	
	def enforceSyntacticalConstraints(self, r, tokens):
		tags = [part[1] for part in tokens[r[0]:r[1]+1]]
		words = [part[0] for part in tokens[r[0]:r[1]+1]]
		
		# check the two stop list syntactical Constraints
		firstVerbFound = False
		for tag in tags:
			if tag in self.v2 and firstVerbFound != True:
				if tag in ['VBG', 'VBN']:
					return False
				else:
					firstVerbFound = True
					
			if tag in self.stopTags:
				return False
		
		for word in words:
			if word in self.stopWords:
				return False
		
		if tokens[r[0]-1][1] in ['EX','TO']:
			return False
		
		return True
		
	
	def collapseRelations(self, tokens):
		ends = []
		for e in self.ePoints:
			if len(ends) == 0:
				ends.append(e)
				continue
			if e[0]-1 <= ends[len(ends)-1][1]: # minus one added to comensate for set right 
				ends[len(ends)-1][1] = e[1]
			else:
				if self.enforceSyntacticalConstraints(e, tokens):
					ends.append(e)

		return ends
	
	def findEnd(self, tokens, s): # s is the start of the relational phrase - at this point we're always at v2
		
		# take into account the start as i cannot just be passed out of the function - it must be i+ (s+1)
		# also, all of length checks should take into account that i is now a relative number...  so it must be checking i + (s+1)
		
		if s == len(tokens)-1: # if the last word of the sentence is passed
			return False 
			
		i = s+1 # sets i to the next token beyond the first hit for the relationship
			
		if tokens[i][1] not in self.v3 and tokens[i][1] not in self.p2 and tokens[i][1] not in self.w1: # could also be in p1, but as p1 and v3 are identical I only check 1
			return i-1 # found the end of the simple relational phrase v1? -> v2
			
		if tokens[i][1] in self.p2 and tokens[i][1] != 'RP': # if the token is 'RP' then it could either be in v3 or p2 - So maybe process it both ways? - this function assumes it's a p2 match...

			if i < len(tokens)-1: #meaning this is not the last word...
				if tokens[i+1][1] in self.p3 and i+1 < len(tokens)-1:
					return i+1 # found the end of the relationship v1? -> v2 -> p2 -> p3
				elif tokens[i+1][1] in self.p3:
					return False # would only be true if tokens[i+1] is the last word in the sentence - and there would be no noun, so false
				else:
					return (i) # found the end of the relationship v1? -> v2 -> p2 (neither v3, p1, or p3 were present)
			else:
				return False # if the found match is the last word - there's no room for a noun
			
			
		if tokens[i][1] in self.v3: # doesn't necessarily imply v1? -> v2 -> v3, could also be v1? -> v2 -> w or v1? -> v2 -> p1 (will need to look ahead next to disambiguate)
			self.ePoints.append([s,i])
			if i < len(tokens)-1: # make sure this isn't the last word
				if tokens[i+1][1] in self.p2 and i+1 < len(tokens)-1: # v1? -> v2 -> v3 -> p2 or v1? -> v2 -> p1 -> p2
					if tokens[i+2][1] in self.p3 and i+2 < len(tokens)-1:
						return i+2 # v1? -> v2 -> v3 -> p2 -> p3 (or) v1? -> v2 -> p1 -> p2 -> p3
					elif tokens[i+2][1] in self.p3:
						return False # found a match, but it's the last word, so no relationship here
					else:
						return i+1 # found a match for v1? -> v2 -> v3 -> p2 (or) v1? -> v2 -> p1 -> p2
					
				elif tokens[i+1][1] == 'RB': # could mean we're currently matching w1 or p1 - so we'll need to look ahead to find out
					if i+2 < len(tokens)-1:
						if tokens[i+2][1] in self.p2: # now we've matched v1? -> v2 -> v3 -> p1 -> p2
							if tokens[i+3][1] in self.p3 and i+3 < len(tokens)-1:
								return i+3 # v1? -> v2 -> v3 -> p1 -> p2 -> p3
							elif tokens[i+3][1] in self.p3:
								return False # has to be the last word - so there can't be any noun next...
							else:
								return i+2 # v1? -> v2 -> v3 -> p1 -> p2
						elif tokens[i+2][1] in self.w1:
							return self.processW(tokens, i+1) # v1? -> v2 -> v3[i] -> w1[i+1](RB) -> w1 # process one behind, because the latest match could be for w or for p after a single w
					else:
						return False		
					
				elif tokens[i+1][1] in self.w1:
					return self.processW(tokens, i+1) # v1? -> v2 -> v3 -> w1
			else:
				return False
			
		elif tokens[i][1] in self.w1:
			return self.processW(tokens, i) # v1? -> v2 -> w1 (where the w1 match is unambiguous - not 'RB')
			
		else:
			return False # return False if no meaningful extraction can be made
	
	def processW(self, tokens, s):
		if s+1 >= len(tokens)-1: # cannot be next to last or last word (there must be a match for p2 for the relationship to be valid)
			return False
		for i, word in enumerate(tokens[s+1:]):
			if word[1] in self.p2:
				if (s+1)+i+1 < len(tokens)-1:
					if tokens[(s+1)+i+1][1] in self.p3 :
						return (s+1)+i+1 # w1 -> p2 -> p3
					else:
						return (s+1)+i # w1 -> p2
				else:
					return False # this means it's the last word - not a valid relation
			if word[1] in self.w1:
				continue
			if word[1] not in self.w1 and word[1] not in self.p2:
				return False
		return False
				
			


###########################		
# Assemble Relationships
#
# Here both the Noun-Phrases and the Relational Phrases should be parsed
# so all that's necessary is to assemble the final relationships and 
# do some simple noun-phrase conversion to handle compound noun-phrases
# and draw proper relationship between disparet noun-phrases

class assembleNounPhrases():
	
	def __init__(self):
		self.cc = set(['CC', 'LS']) # signals that the noun phrases should both relate to the target of the relational phrase
		self.co = ['IN'] # conjunction - signals the Noun Phrases should relate to one another - but not both to the other part of the rel phrase
	
	def returnRelationships(self, tokens, rPhrases, nPhrases):
		
		self.relations = []
		
		#start with the relational phrases and work your way out from there...
		start = 0
		for i, r in enumerate(rPhrases):
			# find the left noun phrase...
			if i == 0:
				leftNP = self.findLeftNP(0,r[0], tokens, nPhrases)
			else:
				leftNP = self.findLeftNP(rPhrases[i-1][1]+1,r[0], tokens, nPhrases)
			# find the right noun phrase...
			if i < len(rPhrases)-1: # means that this is not the last relational phrase
				rightNP = self.findRightNP(r[1]+1, rPhrases[i+1][0], tokens, nPhrases) # looking should be inclusive of the left boundary - but exclusive of the right i >= left, i < right
			else:
				rightNP = self.findRightNP(r[1]+1, len(tokens)-1, tokens, nPhrases) # in this case the right boundary for the right NP should be the last token in the sentence
				
			if leftNP and rightNP:
				for lr in leftNP:
					for rr in rightNP:
						self.relations.append([tokens[lr[0]:lr[1]+1],
										  	   tokens[rr[0]:rr[1]+1],
										  	   tokens[r[0]:r[1]+1]])
		return self.relations
	
	
	
	def findRightNP(self, leftB, rightB, tokens, nPhrases):
		# first filter the noun-phrases to figure out the possible candidates
		
		candidatePhrases = []
		
		for nP in nPhrases:
			if nP[0] >= leftB and nP[1] < rightB:
				candidatePhrases.append(nP)
		
		if len(candidatePhrases) == 1:
			return [candidatePhrases[0]]
		
		if len(candidatePhrases) < 1:
			return False
		
		if len(candidatePhrases) > 1: # this is the difficult case where NPs need to be resolved...
			phraseSet = []
			
			for i, np in enumerate(candidatePhrases):
				if i == 0:
					phraseSet.append(np)
				if i > 0:
					connection = tokens[phraseSet[len(phraseSet)-1][1]+1:np[0]]
					tagSet = set([p[1] for p in connection])
					if tagSet.issubset(self.cc):
						phraseSet.append(np)
					elif tagSet.issubset(self.co):
						self.relations.append([tokens[ phraseSet[len(phraseSet)-1][0] : phraseSet[len(phraseSet)-1][1]+1], 
											   tokens[np[0]:np[1]+1], connection])
						# in this case the desired word will already be appending onto the phraseSet - so no action is necessary
					else:
						return phraseSet

			return phraseSet
				
		
			
	def findLeftNP(self, leftB, rightB, tokens, nPhrases):
		# first filter the noun-phrases to figure out the possible candidates
		candidatePhrases = []
		
		for nP in nPhrases:
			if nP[0] >= leftB and nP[1] < rightB:
				candidatePhrases.append(nP)
		
		if len(candidatePhrases) == 1:
			return [candidatePhrases[0]]
		
		if len(candidatePhrases) < 1:
			return False
		
		if len(candidatePhrases) > 1: # this is the difficult case where NPs need to be resolved...
			phraseSet = []
			for i, np in enumerate(reversed(candidatePhrases)):
				if i == 0:
					phraseSet.append(np)
				if i > 0:
					connection = tokens[np[1]+1:phraseSet[len(phraseSet)-1][0]]
					tagSet = set([p[1] for p in connection])
					if tagSet.issubset(self.cc):
						phraseSet.append(np)
					elif tagSet.issubset(self.co):
						self.relations.append([tokens[ phraseSet[len(phraseSet)-1][0] : phraseSet[len(phraseSet)-1][1]+1], 
											   tokens[np[0] : np[1]+1] , connection])
						# then replace the last NP with the current one and continue to check for and type clauses...
						phraseSet[len(phraseSet)-1] = np
					else: # the case that some other arbitrary connection is being made - just return what you have...
						return phraseSet
			return phraseSet 
		
		
	

#####################
# Noun Phrase identifier via Conll2002 and trained chunker

class ChunkParser(nltk.ChunkParserI):
	
	def __init__(self, train_sents):
		train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)] for sent in train_sents]
		self.tagger = nltk.TrigramTagger(train_data)
	
	def parse(self, sentence):
		pos_tags = [pos for (word, pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)

		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		
		relBounds = []
		
		start = -1
		for i, ctag in enumerate(chunktags):
			if ctag == 'B-NP':
				start = i
			if start != -1 and ctag != 'I-NP' and start != i:
				relBounds.append([start, i-1])
				start = -1
		
		if start != -1:
			relBounds.append([start, len(chunktags)-1]) # if the last phrase in a NP - append it
		
		return relBounds
		

	
