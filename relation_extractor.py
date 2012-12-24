from __future__ import division
import nltk, re, pprint

f = open('sample_Huckleberry_Finn.txt')
#f = open('winston_times.txt')
#f = open('enronsent00.txt')
raw = f.read()
outF = open('sentence_segments.txt', 'w')

# Sentences splitting...

sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
sents = sent_tokenizer.tokenize(raw)

taggedSents = []

#for s in sents[100:125]:
#	taggedSents.append(nltk.pos_tag(nltk.word_tokenize(s)))

#print(taggedSents[1][1][1])
#taggedWords = nltk.pos_tag(nltk.word_tokenize(raw))
#a = [pos[1] for pos in taggedWords]
#a = [[pos[1] for pos in word] for word in taggedSents]
#print(set(a))

#outF.write(str(output))
#outF.close()

catV = ['RB', 'RBS', 'RP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'WRB', 'VBZ']
catW = ['DT', 'JJ', 'JJR' 'JJS', 'NN', 'NNP', 'NNPS', 'PDT', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'WDT', 'WP', 'WP$', 'WRB']
catP = ['IN', 'RP', 'TO']

catNP = ['NN', 'NNS', 'NNP', 'NNPS', 'PRP', '$PRP']

rPhrases = []


def handleWP(s, i):
	s = s[i:]
	for i, word in enumerate(s):
		if i == len(s):
			return False
			if word[i] in catP:
				return i+1
	return False


def printRSegments(ends, s):

	print(s)
	print('Relations:')
	for e in ends:
		relation = ''
		for p in s[e[0]:e[1]]:
			relation += p[0] + ' '
		print(relation)
		#rPhrases.append(relation)
	print(' ')
	

## !-- Should find the noun - Phrase(s) before the target relationship...
def findPrevNP(i, ends, s): 
	if ends[i][0] == 0: # if the current relationship is the first word of the sentence...
		return None
	
	# determine the left boundary of the area
	left = 0
	if i > 0:
		left = ends[i-1][1]
	
	right = ends[i][0]
	
	NPs = [] #array to hold the found Noun Pairs...
	for word in s[left:right]:
		if word[1] in catNP:
			NPs.append(word[0])
	if len(NPs) == 0:
		if i > 0:
			return findPrevNP(i-1, ends, s)
		else:
			return None
	return NPs
	
## !-- Finds the next appropriate Noun-Pairs... Afte the relationship given...	
def findNextNP(i, ends, s):
	if ends[i][1] == len(s)-1: #if the relationship stretches all the way to the end of the sentence
		return None
	
	left = ends[i][1]
	
	right = len(s)-1 #initialize the right boundary to last letter of the sentence...
	if i < len(ends)-1: # means that this is not the last relationship of the sentence...
		right = ends[i+1][0]
	
	NPs = []
	for word in s[left:right]:
		if word[1] in catNP:
			NPs.append(word[0])
	if len(NPs) == 0:
		if i < len(ends)-1:
			return findNextNP(i+1, ends, s)
		else:
			return None
	return NPs
		

def extractNPFromRelation(i, ends, s):
	NPs = []
	for word in s[ends[i][0]:ends[i][1]]:
		if word[1] in catNP:
			NPs.append(word)
	if len(NPs):
		return NPs
	return None		
		
		
	
	
def determineNP(ends, s):
	
	relations = [];
	
	for i, e in enumerate(ends):
		r = {}
		r['prevNP'] = findPrevNP(i, ends, s)
		r['nextNP'] = findNextNP(i, ends, s)
		r['addNP'] = extractNPFromRelation(i, ends, s)
		r['relation'] = s[ends[i][0]:ends[i][1]]
		if r['prevNP'] and r['nextNP'] and r['relation']:
			relations.append(r)

	for r in relations:
		#print('prev: ' +str(r['prevNP']) + ' -> next: ' +str(r['nextNP']) + ' additional: ' +str(r['addNP']))
		outF.write('prev: ' +str(r['prevNP']) + ' -> next: ' +str(r['nextNP']) + ' relation: ' +str(r['relation']) + '\n')
	

			
	



def collapsePairs(ePoints):
	ends = []
	for e in ePoints:
		if len(ends) == 0:
			ends.append(e)
			continue
		if e[0] <= ends[len(ends)-1][1]:
			ends[len(ends)-1][1] = e[1]
		else:
			ends.append(e)
	return ends


def findRelations(s):
	ePoints = []
	for i, word in enumerate(s):
		if i == len(s)-1:
			continue
		if word[1] in catV:
			ePoints.append([i, i+1])
			if s[i+1][1] in catP:
				ePoints.append([i, i+2])
			elif s[i+1][1] in catW:
				r = handleWP(s, i+1)
				if r:
					rPoints.append([i, r])
	determineNP(collapsePairs(ePoints), s)

				
		
		
for s in sents:
	findRelations(nltk.pos_tag(nltk.word_tokenize(s)))

outF.close()
print('done')

#print(set(rPhrases))

#print(sents[101:102])

#print(catV)