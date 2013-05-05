class SpellingTrie(object):
	def __init__(self):
		self.dict_database = {}
		#Import words from the Linux dictionary
		try:
			imported_dictionary = open('/usr/share/dict/words')
			raw_imported_lines = imported_dictionary.readlines()
		except:
			print "ERROR: DICTIONARY NOT FOUND ON COMPUTER."
		
		#Create the trie from the imported words.
		self.word_size = 0
		self.char_size = 0
		for word in raw_imported_lines:
			word = word[:-1] #Remove the "/n" character from the word.
			
			if len(word)==1 and not word in "ai":
				pass #Don't add single consonants/vowels to trie if not true words
			else:
				self.add_word(word)
		print "{} words integrated into trie!".format(self.word_size)
		
	def add_word(self, new_word, first_call=True):
		#Start creating new "nodes" from the top of the database.
		if first_call: 
			self.current_tier = self.dict_database			
			self.word_size += 1
			
		self.char_size += 1
		if len(new_word)==1:
			#Mark a possible ending with the key/val pair, {"*":"*"}
			self.current_tier[new_word[0]] = {"*":"*"}
		else:
			try:
				#Check if a key already exists.
				self.current_tier[new_word[0]]
			except:
				#If a key doesn't exist, create it.
				self.current_tier[new_word[0]] = {} 
			self.current_tier = self.current_tier[new_word[0]] #Move further down the trie.
			self.add_word(new_word[1:], False) #Recursively the rest of the word to the trie.
			
	def size(self, option = "word"):
		if option.lower()=="word":
			return self.word_size				
		elif option.lower()=="char":
			return self.char_size
		else:
			raise Exception("ERROR: Please use \"word\" or \"char\".")
			
	def contains(self, word):
		try:
			self.current_tier = self.dict_database
			while (len(word)>1):
				self.current_tier = self.current_tier[word[0]]
				word = word[1:]
			return "*" in self.current_tier[word[0]]
		except: 
			#A spelling does not exist
			return False
			
	def __contains__(self, word):
		return self.contains(word)
		
#Initilialize the Spelling Trie:
print "Now loading spelling trie..."
trie = SpellingTrie()

#Import Other Databases:
from phonetic_library import *

#SPELL-CHECKING FUNCTIONS:		---------------------------------------
def filter_word(raw_word): #Returns "filtered" string
	try:
		assert(type(raw_word)==type(""))
		word = ""
		for character in raw_word.lower():
			if character in "abcdefghijklmnopqrstuvwxyz'":
				word += character
		return word
	except:
		raise Exception("ERROR: Word must be STRING type.")

def spell_check_word(word): #Returns Boolean
	try:
		assert(type(word)==type(""))
		return filter_word(word) in trie
	except:
		raise Exception("ERROR: Word must be STRING type.")

def spell_check_phrase(raw_data, suggest=False): #Returns Boolean and list of incorrect words
	if type(raw_data)==type(list()):
		list_of_words = raw_data
		misspelled_words = []
		for word in list_of_words:
			word = filter_word(word)
			if not spell_check_word(word) and len(word)>0:
				misspelled_words += [word]
	elif type(raw_data)==type(str()):
		list_of_words = raw_data.split()
		misspelled_words = []
		for word in list_of_words:
			word = filter_word(word)
			if not spell_check_word(word)  and len(word)>0:
				misspelled_words += [word]
	else:
		raise Exception("ERROR: Phrase must be LIST or STRING type.")
	
	if len(misspelled_words) and suggest:
		suggested_words = []
		for word in misspelled_words:
			suggested_words += ["\"{}\" --> \"{}\"".format(word,suggest_word(word))]
		return False, suggested_words
	elif len(misspelled_words):
		return False, misspelled_words
	else:
		return True, []
	
def spell_check_doc(doc, suggest=False):
	try:
		assert(type(doc)==type(""))
		raw_imported_data = open(doc)
		raw_imported_lines = raw_imported_data.readlines()
		list_of_words = ' '.join(raw_imported_lines)
		if suggest:
			return spell_check_phrase(list_of_words,True)
		else:
			return spell_check_phrase(list_of_words)
	except:
		raise Exception("ERROR: File cannot be loaded.")

#SUGGESTION FUNCTIONS:		------------------------------------------
def phonetic_spelling(string, phrases_left): #Returns one correct word as a string
	try:
		assert(type(string)==type(""))
		if len(phrases_left)==0:
			return None
		current_phrase = phrases_left.pop()
		mod_string = string #modified_string
		mod_string = mod_string.replace(current_phrase, phonetic_dict[current_phrase],1)					
		if mod_string in trie: 
			return mod_string
		else:
			return phonetic_spelling(string, phrases_left) or phonetic_spelling(mod_string, phrases_left)
				#else:
				#	return phonetic_spelling(possible_word)
	except:
		raise Exception("ERROR: Word must be STRING type (MISSING).")	
		
def wrong_character(string): #Returns one correct word as a string
	try:
		assert(type(string)==type(""))
		alphabet = "etaoinshrdlcumwfgypbvkjxqz" #Frequency from: http://en.wikipedia.org/wiki/Letter_frequency#Relative_frequencies_of_letters_in_the_English_language
		for i in range(len(string)): ###O(n^2) Grossly slow
			for letter in alphabet:
				possible_word = string[:i] + letter + string[i+1:]					
				if possible_word in trie: 
					return possible_word
	except:
		raise Exception("ERROR: Word must be STRING type (MISSING).")	
		
def missing_character(string): #Returns one correct word as a string
	try:
		assert(type(string)==type(""))
		alphabet = "etaoinshrdlcumwfgypbvkjxqz" #Frequency from: http://en.wikipedia.org/wiki/Letter_frequency#Relative_frequencies_of_letters_in_the_English_language
		for i in range(len(string)): ###O(n^2) Grossly slow
			for letter in alphabet:
				if i==0:
					possible_word = letter + string[i:]
				else:
					possible_word = string[:i] + letter + string[i:]					
				if possible_word in trie: #Only return true words
					return possible_word
	except:
		raise Exception("ERROR: Word must be STRING type (MISSING).")	
		
def extra_character(string): #Returns one correct word as a string
	try:
		assert(type(string)==type(""))
		for i in range(len(string)): 
			if i == len(string)-1:
				possible_word = string[:i]
			else:
				possible_word = string[:i] + string[i+1:]
			if possible_word in trie: #Only return true words
				return possible_word
	except:
		raise Exception("ERROR: Word must be STRING type (MISSING).")	
		
def flipped_characters(string): #Returns one correct word as a string
	try:
		assert(type(string)==type(""))
		possible_word = ""
		for i in range(len(string)):
			if i+2<len(string): #If the string has characters following the "flipped" characters
				possible_word = string[:i]+string[i+1]+string[i]+string[i+2:]
			elif i+1<len(string):
				possible_word = string[:i]+string[i+1]+string[i]
			else:
				pass 
			
			if possible_word in trie: #Only return true words
				return possible_word
	except:
		raise Exception("ERROR: Word must be STRING type (FLIPPED).")	
	
	
def space_forgotten(string): #Returns two correct words as strings delineated by a space.
	try:
		assert(type(string)==type(""))
		for i in range(len(string)):
			left_half = string[:i]
			right_half = string[i:]
			if left_half in trie and right_half in trie:
				return left_half + " " + right_half
	except:
		raise Exception("ERROR: Word must be STRING type (SPACE).")

def suggest_word(string): #Returns a list of suggested words (as strings).
	try:
		assert(type(string)==type(""))
		list_of_suggestions = []
		
		temp0 = phonetic_spelling(string, phonetic_dict.keys())
		if temp0:
			list_of_suggestions += [temp0]
					
		temp1 = flipped_characters(string)
		if temp1: list_of_suggestions += [temp1]
			
		temp2 = missing_character(string)
		if temp2: list_of_suggestions += [temp2]
					
		temp3 = extra_character(string)
		if temp3: list_of_suggestions += [temp3]
					
		temp4 = wrong_character(string)
		if temp4: list_of_suggestions += [temp4]
					
		temp5 = space_forgotten(string)
		if temp5: list_of_suggestions += [temp5]

		if len(list_of_suggestions):
			return list_of_suggestions
		else:
			return None	
		"""
		#Doesn't enumerate all possible words:
		temp = phonetic_spelling(string, phonetic_dict.keys())
		if temp: return temp
		
		temp = flipped_characters(string)
		if temp: return temp
		
		temp = missing_character(string)
		if temp: return temp
		
		temp = extra_character(string)
		if temp: return temp
		
		temp = wrong_character(string)
		if temp: return temp
		
		temp = space_forgotten(string)
		if temp: return temp
		"""
		
	except:
		raise Exception("ERROR: Word must be STRING type.")
		
		
		
		
#TEST SUITE -- Casey Falk:
print "__"*10
print "Checking spelling of individual words:"
print "--Contains \"car\" -->", trie.contains("car") #True
print "--Contains \"z\" -->", trie.contains("z") #True
print "--Contains \"apothec\" -->", trie.contains("apothec") #True
print "--Contains \"card\" -->",trie.contains("card") #True
print "--Contains \"caRd\" -->",trie.contains("caRd") #True
print "--Contains \"cargh\" -->",trie.contains("cargh") #False

print "__"*10
print "Checking spelling of phrases:"
a = "This is a true phrase."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #True
a = "This is a false phrasehg."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #False
a = "Thise ias akso ae ffalse phrasehg."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #False
a = "....."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #True (actually empty)
a = ""
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #True (empty)
a = "... !!\n.."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #True (actually empty)
a = ["this,", "IS", "My.", "favorite", "prOGram"]
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #True (according to character patterns)
a = ["this,", "IS", "My.a", "favorite", "prOGram"] ###Should "My.a" split to ["my", "a"] or ["mya"]?
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #False (according to character patterns)
a = "Thise phfrase isn'ty spelled very well."
print "--\"{}\" --> {}".format(a,spell_check_phrase(a)) #False (according to character patterns)

print "__"*10
print "Offer word spelling suggestions:"
a = "helloworld"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "teh"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "tehm"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "pengin"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "pengui"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "enguin"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "penguinr"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "pengguin"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "hebgyubu"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))### Not conquered.
a = "z"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "o"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "garentee"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "garenti"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "filosofer"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "Incidently"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "basicly"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))
a = "accidently"
print "--Suggestion for \"{}\" --> \"{}\"".format(a,suggest_word(a))

print "__"*10
print "Offer phrase spelling suggestions:"

a = "Thise phfrase isn'ty spelled very well."
b = spell_check_phrase(a, True)
print "--\"{}\" --> {}".format(a,b[0]) #False (according to character patterns)
for suggestion in b[1]: print "     ",suggestion 

a = "This phrase is correctly spelled."
b = spell_check_phrase(a, True)
print "--\"{}\" --> {}".format(a,b[0]) #False (according to character patterns)
for suggestion in b[1]: print "     ",suggestion 

print "__"*10
print "Test document:"
a = "/home/cfalk/Documents/Python_Stuff/spell_check_test_doc"
print "FILE PATH: {}".format(a)
b = spell_check_doc(a,True)
print "BOOLEAN RESULT: {}".format(b[0])
for suggestion in b[1]: 
	if suggestion[-6:] == "\"None\"":
		print "     {} ----- NEED TO FINISH".format(suggestion)
	else: 
		print "     {}".format(suggestion) 
		
print "__"*10
print "User Interface: (CTRL+C TO TERMINATE)"
while True:
	raw_data = str(raw_input("Please input a string to check:\n--"))
	print "RESULTS:",spell_check_phrase(raw_data, True),"\n"
