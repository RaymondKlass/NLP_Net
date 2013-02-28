import pymongo
from pymongo import MongoClient



class nltkHelper:

	def __init__(self):
		self.location = None
		self.bootstrapSentSplitter()
		self.bootstrapTokenizer()
	
	
	def bootstrapSentSplitter(self):
		self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	
	
	def bootStrapTokenizer(self):
		self.tokenize = nltk.word_tokenize
		self.pos_tag = nltk.pos_tag
	
	
	def insertRaw(self, rawText): # this is the main function to insert new text into the system...
		self.raw = rawText
		
		#Split the document into sentences - for now we assume relatively small files - we'll use streaming for really large files.
		self.sents = self.sent_tokenizer.tokenize(self.raw)
		
		for sent in self.sents:
			self.tokenized = self.pos_tag(self.tokenize(sent))
			print(self.tokenized)






	
nlp = nltkHelper()
nlp.insertTextFile('hello, this is a sample sentence...')