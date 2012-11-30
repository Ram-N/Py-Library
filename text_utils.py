import re
from nltk.corpus import wordnet as wn
import nltk
from nltk.corpus import brown
from nltk.probability import *
from collections import defaultdict #automatically initializes to zero

# Contains common utility functions used to solve NPR word puzzles

# http://idrisr.wordpress.com/2011/02/01/npr-puzzle-finding-synonyms-with-python-and-wordnet/


def meaning(oneword):
    """ store the meaning in a list """
    mean = []
    for word_meaning in wn.synsets(oneword):
        mean.append(word_meaning.definition)

    return(mean)


def print_words_with_meanings(matches):

    for m in matches:
        if meaning(m): #print only those words whose meaning is known
            #TODO: select the "most relevant" meaning. Going with the first one for now
            print m, meaning(m)[0] #this needs to be improved. 



def subset_list_of_words_to_those_with_meaning(wordList, wordlimit=False):
    '''
    Take a list of English words. Cut out the ones whose meaning is not known towordnet English dictionary 
    '''
    wList = []
    numWords = 0

    for w in wordList:        
        if meaning(w): #include only those words whose meaning is known
            #TODO: select the "most relevant" meaning. Going with the first one for now
            numWords += 1
            wList.append(w)
            if wordlimit and numWords ==100: #take up to first 100 matches
                break

    print numWords, "Words with meanings"
    return wList


def sort_word(word):
    """sorts word and removes white spaces"""
    l = [letter for letter in word]
    l.sort(reverse=False)
    sort_word = ''.join([letter for letter in l])
    return sort_word

def swap_letter(s, letter, index):
    """takes a string 's' and replaces s['index'] with 'letter"""
    s = s[:index] + letter + s[index+1:]
    return s

def has_string(big_word, small_word):
    """returns boolean of whether small_word contained in big_word"""
    return -1<>big_word.find(small_word)

def is_len(_iter, length):
    """return boolean of whether '_iter' is length of 'length'"""
    return len(_iter)==length

def permutate(seq):
    """permutate a sequence and return a list of the permutations"""

    # To Do: create another version which only returns perms that are in dictioary

    # To Do: Change to return a unique list of perms
    if not seq:
        return [seq]  # is an empty sequence
    else:
        temp = []
        for k in range(len(seq)):
            part = seq[:k] + seq[k+1:]
            for m in permutate(part):
                x=seq[k:k+1] + m
                temp.append(x)
        return temp

#from github idrisr/wordlist
def load_word_dictionary(path='CROSSWD.TXT'):
    """takes "path" that is path of word list file. Function assumes one word per line.
    White space and capitalization stripped out.  returns dictionary of words with key=word, and value=None"""
    f = open(path, 'r')
    d= dict()
    for line in f.readlines():
        d[line.strip().lower()] = None
    return d

def load_dictionary(path='CROSSWD.TXT'): #as a list
    """takes "path" that is path of word list file. Function assumes one word per line.
    White space and capitalization stripped out.  returns List of words"""
    d= open(path, 'r').read().splitlines()
    return d

def check_synonym(word, word2):
    """checks to see if word2 is a synonym of word2"""
    l_syns = list()
    synsets = wn.synsets(word)
    for synset in synsets:
        if word2 in synset.lemma_names:
            l_syns.append( (word, word2) )
    return l_syns

def ends_with_letter(word, letter):
    """takes "word" and tests to see if last letter is 'letter'"""
    if len(word)>0:
        return word[-1] == letter
    else:
        return False

def split_word_once(word, min_char=2):
    """takes a word and splits it into two segments, with at least 'min_char' in
    each segment. Stores segment in a list, and ultimately returns a list of the
    segment lists"""
    l_segments = list()
    for split in range(min_char, len(word) - min_char + 1):
        l_segment = list()
        l_segment.append( word[:split] )
        l_segment.append( word[split:] )
        l_segments.append( l_segment ) 

    return l_segments

def word_in_dict(word, d):
    return word in d



def searchDictFor(dictionary,regpattern,minLength=1,maxLength=15,plurals=False):
    ''' returns a List of MatchingWords from the dictionary
    given a regEx and a pattern
    '''

    print "Searching for",regpattern
    matchingWords = []

    matchcount = 0
    reg = re.compile(regpattern, re.I) #what does this do?
    m = ""
    for word in dictionary:
        m = reg.match(word)
        if m:
            wlen = word.__len__()
            if wlen<=maxLength and wlen>=minLength:

                # outfile.write(m.group()+' ')
                matchcount += 1            
                # print "Found ",matchcount, word 
                #type(word).__name__
                matchingWords.append(word)

    print "Found ",matchcount, "pattern matches" 
    return matchingWords


def remove_br_slash_tag(data):
    '''
    Utility function to remove <br />from a given string
    '''
    p = re.compile(r'<br />') #the pattern as compiled regex object
    return p.sub('"', data)

def remove_italics_html_tag(data):
    '''
    Utility function to remove <i> and </i> from a given string
    '''
    p = re.compile(r'</?i>') #the pattern as compiled regex object
    return p.sub('"', data)

def remove_backslash_apostrophe(datastr):
    '''
    Utility function to remove the backslash (\)  from a given \' string
    These show up in parsed HTML strings
    '''
    p = re.compile(r"\\\'") #the pattern as compiled regex object
    return p.sub("'", datastr)


# from http://stackoverflow.com/questions/5928704/how-do-i-find-the-frequency-count-of-a-word-in-english-using-wordnet
def word_frequency(word):
    '''
    In WordNet, every Lemma has a frequency count that is returned by the method lemma.count() and that is stored in the file nltk_data/corpora/wordnet/cntlist.rev.
    This function accesses that frequency count.
    '''
    syns = wn.synsets(word)
    for s in syns:
        for l in s.lemmas:
            print l.name + " " + str(l.count())



def brown_corpus_word_frequency(targetWord):
    words = FreqDist()

    for sentence in brown.sents():
        for word in sentence:
            words.inc(word.lower())

    print words[targetWord]
    print words.freq(targetWord)


def createListWithWordCounts_fromString(longString):
    

    d = defaultdict(int)
    for word in longString.split():
        d[word] += 1

    sortedList = [(k,v) for k,v in d.items()]
    sortedList = sortedList.sort(reverse=True)
    return sortedList
