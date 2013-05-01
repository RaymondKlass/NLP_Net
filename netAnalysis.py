from __future__ import division
import nltk, re, pprint
import operator
import sys, time
import cPickle


#### -- Load the pickle that contains the word - to - word relationships

FILE = open('output/Output_all_new_combo_all' +'.char', 'rb')
fileContents = cPickle.load(FILE)
FILE.close()


#### -- Define the analysis functions here...

def singleWordAnalysis(w, fileContents):
	try:
		a = fileContents[w].keys()
	except:
		print 'Word not found'
		return False
	
	
	print 'Length: ' + str(len(fileContents[w]))
	dListSorted = sorted(fileContents[w].iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass
	

def doubleWordAnalysis(w1, w2, fileContents):
	
	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])

	dList = {}

	for r in word1:
		 if r in word2:
			try:
				dList[r] = (word1[r] + word2[r]) / sum(fileContents[r].values())
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass


def doubleWordAnalysis2(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	bigStart = time.time()
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = (word1[r] + word2[r])
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass


def doubleWordAnalysis3(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = (word1[r] + word2[r]) * ((word1[r] + word2[r]) / sum(fileContents[r].values()))
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass
	
def doubleWordAnalysis4(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	bigStart = time.time()
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = (word1[r] + word2[r]) * ((word1[r] + word2[r]) / (sum(fileContents[r].values())/5)  )
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass
	
def doubleWordAnalysis5(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	rSum = sum(fileContents[w1].values())
	wSum = sum(fileContents[w2].values())
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = ((word1[r] / rSum) + (word2[r] / wSum)) 
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass
	
def doubleWordAnalysis6(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	bigStart = time.time()
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	rSum = sum(fileContents[w1].values())
	wSum = sum(fileContents[w2].values())
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = ((word1[r] / rSum) + (word2[r] / wSum)) * ((word1[r] + word2[r]) / (sum(fileContents[r].values()))) / 2 # the 3 is for dampening
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass
	
def doubleWordAnalysis7(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])

	dList = {}
	
	rSum = sum(fileContents[w1].values())
	wSum = sum(fileContents[w2].values())
	
	for r in word1:
		 if r in word2:
			try:
				val = ((word1[r] / rSum) + (word2[r] / wSum)) * ((word1[r] + word2[r]) / (sum(fileContents[r].values()))) / 2 # the 3 is for dampening
				if sum(fileContents[r].values()) > 1000:
					dList[r] = val
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass

def doubleWordAnalysis8(w1, w2, fileContents):

	try:
		a = fileContents[w1].keys()
		a = fileContents[w2].keys()
	except:
		print 'Word not found'
		return False
	
	bigStart = time.time()
	
	print 'Length of ' + str(w1) + ': ' + str(len(fileContents[w1]))
	print 'Length of ' + str(w2) + ': ' + str(len(fileContents[w2]))
	
	word1 = dict(fileContents[w1])
	word2 = dict(fileContents[w2])
	
	dList = {}
	
	rSum = sum(fileContents[w1].values())
	wSum = sum(fileContents[w2].values())
	
	for r in word1:
		 if r in word2:
			try:
				dList[r] = ((word1[r] / rSum) + (word2[r] / wSum)) - (abs(word1[r] - word2[r])) / 2
			except:
				pass
	
	dListSorted = sorted(dList.iteritems(), key = operator.itemgetter(1), reverse=True)
	for i in range(50):
		try:
			print dListSorted[i]
		except:
			pass

#### -- Controlling program here...

while(True):
	
	print 'Net Analysis Menu:'
	print '1: Evaluate a single word'
	print '2: Evaluate 2 words - scored proportional to words total links'
	print '3: Evaluate 2 words - sum of word occurances'
	print '4: Evaluate 2 words - hybrid proportional and total num occurances'
	print '5: Evaluate 2 words - hybrid proportional and total num occurances less 5'
	print '6: Evaluate 2 words - normalize per word'
	print '7: Evaluate 2 words - normalized + dampening'
	print '8: Evaluate 2 words - normalized + dampening + min density 1000'
	print '9: Evaluate 2 words - normalize per word with reward for similarity'
	print '1: Press to exit'
	print ''
	try:
		inputValue = int(raw_input('Please choose an option: '))
	except:
		inputValue = 1
		pass
	
	if inputValue is 10:
		break
	
	if inputValue is 1:
		print ''
		input2 = raw_input('Please enter a single word to evaluate: ')
		# evaluate word here...
		singleWordAnalysis(input2, fileContents)
	
	elif inputValue is 2:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis(input2, input3, fileContents)
		
	elif inputValue is 3:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis2(input2, input3, fileContents)
	elif inputValue is 4:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis3(input2, input3, fileContents)
	elif inputValue is 5:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis4(input2, input3, fileContents)
	elif inputValue is 6:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis5(input2, input3, fileContents)
	elif inputValue is 7:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis6(input2, input3, fileContents)
	elif inputValue is 8:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis7(input2, input3, fileContents)
	elif inputValue is 9:
		print ''
		input2 = raw_input('Please enter the first word of 2: ')
		input3 = raw_input('Please enter the second word of 2: ')
		#evaluate 2 word pair here...
		doubleWordAnalysis8(input2, input3, fileContents)
		
#### -- end controlling program logic...