"""Main PyQuran Library  Module

* Data: Sat Nov 18 03:30:41 EET 2017

This module contains tools for `Quranic Analysis`
(More expressive description later)

"""
# Adding another searching path
from sys import path
import os

# The current path of the current module.
path_current_module = os.path.dirname(os.path.abspath(__file__))
tools_modules = '../tools/'
tools_path = os.path.join(path_current_module, tools_modules)

path.append(tools_path)




import quran
import sys
import error
import numpy
import operator
import re
import searchHelper
import functools
import difflib as dif
import arabic
from arabic import *
from pyarabic.araby import strip_tashkeel, strip_tatweel,separate,strip_tatweel

from audioop import reverse
from itertools import chain
from collections import Counter, defaultdict


import buckwalter
import sys
import shapeHelper
from collections import OrderedDict

from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree
from xml.dom import minidom

def parse_sura(sura_number, alphabets=['ل', 'ب']):
    """parses the sura and returns a matrix (ndarray),
    the rows number equals to the ayat number,
    and the columns number equals to the length of alphabets

    What it does:
        it calculates number of occurrences of each on of letters
        in the alphabets for each aya.

        If `A` is a ndarray,
        then A[i,j] is the number of occurrences of the letter
        alphabets[j] in the aya i.

    Args:
        sura_number: 1 <= Integer <= 114, the ordered number of sura in Mushaf.
        alphabets: a list of alphabets

    Returns:
        ndarray: with dimensions (a * m), where
        `a` is the number of ayat el-sura and
        `m` is the number of letters passed to the function through alphabets[]

    Note:
        1. A list of Arabic letters maybe flipped by your editor,
           so, the first char will be the most-right one,
           unlike a list of English char, the first element
           is the left-most one.

        2. I didn't make alphabets[] 29 by default.
           Just try it by filling the alphabets with some letters.

    """
    # getting the nth sura
    sura  = quran.get_sura(sura_number)
    # getting the ndarray dimensions
    a = len(sura)
    m = len(alphabets)
    # building ndarray with appropriate dimensions
    A = numpy.zeros((a,m), dtype=numpy.int)


    # Filling ndarray with alphabets[] occurrences
    i = 0 # number of current aya
    j = 0 # occurrences
    for aya in sura:
        for letter in alphabets:
            A[i,j] = aya.count(letter)
            j += 1
        j = 0
        i += 1

    return A





def get_frequency(sentence):
    """it takes sentence that you want to compute it's
       words frequency.

    Args:
        sentence: String, represents sentence that wanted to compute it's words frequency.

    Returns:
        dict: {str: int}

    Example:
    ```python
    q.get_frequency(q.quran.get_verse(1,1))\n
	
    >>> {'الرحمن': 1, 'الرحيم': 1, 'الله': 1, 'بسم': 1}
    ```
    """
    if type(sentence) != str:
        raise TypeError('sentece should be string')
    # split sentence to words
    word_list = sentence.split()
    #compute count of uniqe words
    frequency = Counter(word_list)
    #sort frequency descending
    sorted_freq = dict(sorted(frequency.items(),key=operator.itemgetter(1),reverse=True))
    return sorted_freq



def generate_frequency_dictionary(suraNumber=None):
    """It takes a number of  sura,then order ot and returns the dictionary:
       * **key** is the word and  **value** is a frequency in the Sura.
       - If you don't pass any parameter, then the target will be  **all Quran**.
       - This function have to work on the Quran with تشكيل, because it's an..
         important factor.

    Args:
        suraNumber: Optional, 1 <= Integer <= 114, the ordered number of sura in Mushaf.

    Returns:
        dict: {str: int}

    Example:
    ```python
    q.generate_frequency_dictionary(114)\n
	
    >>> {'أعوذ': 1, 'إله': 1, 'الجنة': 1, 'الخناس': 1, 'الذى': 1, 'الناس': 4, 'الوسواس': 1, 'برب': 1, 'شر': 1, 'صدور': 1, 'فى': 1, 'قل': 1, 'ملك': 1, 'من': 2, 'والناس': 1, 'يوسوس': 1}
    ```
    """
    if type(suraNumber) != int and suraNumber != None :
        raise TypeError('suraNumber should be integer')
    if suraNumber <=0 or suraNumber > arabic.swar_num:
        raise ValueError('suraNumber should be in range [1-114]')

    frequency = {}
    #get all Quran if suraNumber is None
    if suraNumber == None:
        #get all Quran as one sentence
        Quran = ' '.join([' '.join(quran.get_sura(i)) for i in range(1,115)])
        #get all Quran frequency
        frequency=get_frequency(Quran)
    #get frequency of suraNumber
    else:
        #get sura from QuranCorpus
        sura = quran.get_sura(sura_number=suraNumber)
        ayat = ' '.join(sura)
        #get frequency of sura
        frequency = get_frequency(ayat)

    return frequency


def check_sura_with_frequency(sura_num,freq_dec):
    """this function check if frequency dictionary of specific sura is
    compatible with original sura in shapes count

    Args:
        suraNumber: Optional, 1 <= Integer <= 114, the ordered number of sura in Mushaf.

    Returns:
        Boolean: True if compatible, otherwise Flase.
    
	Example:
    ```python
    frequency_dic = q.generate_frequency_dictionary(114)
    q.check_sura_with_frequency(frequency_dic)\n
	
    >>> True
    ```
    """
    if type(sura_num) != int:
        raise TypeError('sura_num should be integer')
    if type(freq_dec) != dict:
        raise TypeError('freq_dec should be dictionary')
    if sura_num <=0:
        raise ValueError('sura_num should be in range [1-114]')

    #get number of chars in frequency dec
    num_of_chars_in_dec = sum([len(word)*count for word,count in freq_dec.items()])
    #get number of chars in  original sura
    num_of_chars_in_sura = sum([len(aya.replace(' ',''))  for aya in quran.get_sura(sura_num)])
    # print(num_of_chars_in_dec ,"    ", num_of_chars_in_sura)
    if num_of_chars_in_dec == num_of_chars_in_sura:
        return True
    else:
        return False





def sort_dictionary_by_similarity(frequency_dictionary,threshold=0.8):
    """this function using to cluster words using similarity
    and sort every bunch of word  by most common and sort bunches
    descending in same time

    Args:
        frequency_dictionary: Dictionary, frequency dictionary that needs to be sorted
		
    Returns:
        dict : {str: int} sorted dictionary
    
    Example:
    ```python
    frequency_dic = q.generate_frequency_dictionary(114)
    q.sort_dictionary_by_similarity(frequency_dic)
    # this dictionary is sorted using similarity 0.8 
	
    >>> {'أعوذ': 1, 'إذا': 2, 'العقد': 1, 'الفلق': 1, 'النفثت': 1, 'برب': 1, 'حاسد': 1, 'حسد': 1, 'خلق': 1, 'شر': 4, 'غاسق': 1, 'فى': 1, 'قل': 1, 'ما': 1, 'من': 1, 'وقب': 1, 'ومن': 3}
    ```
    """
    if type(threshold) != float:
        raise TypeError('threshold should be float')
    if type(frequency_dictionary) != dict:
        raise TypeError('frequency_dictionary should be dictionary')
    if threshold < 0 or threshold > 1:
        raise ValueError('threshold should be float number in range [0-1]')

    # list of dictionaries and every dictionary has similar words and we will call every dictionary as 'X'
    list_of_dics = []
    # this dictionary key is a position of 'X' and value the sum of frequencies of 'X'
    list_of_dics_counts = dict()
    #counter of X's
    dic_num=0
    #lock list used to lock word that added in 'X'
    occurrence_list = set()
    #loop on all words to cluster them
    for word,count in frequency_dictionary.items():
        #check if word is locked from some 'X' or not
        if word not in occurrence_list:
            #this use to sum all of frequencies of this 'X'
            sum_of_freqs = count
            #create new 'X' and add the first word
            sub_dic = dict({word:count})
            #add word in occurrence list to lock it
            occurrence_list.add(word)
            #loop in the rest word to get similar word
            for sub_word,sub_count in frequency_dictionary.items():
                #check if word lock or not
                if sub_word not in occurrence_list:
                    #compute similarity probability
                    similarity_prob = dif.SequenceMatcher(None,word,sub_word).ratio()
                    # check if prob of word is bigger than threshold or not
                    if similarity_prob >= threshold:
                        #add sub_word as a new word in this 'X'
                        sub_dic[sub_word] = sub_count
                        # lock this new word
                        occurrence_list.add(sub_word)
                        # add the frequency of this new word to sum_of_freqs
                        sum_of_freqs +=sub_count
            #append 'X' in list of dictionaries
            list_of_dics.append(sub_dic)
            #append position and summation of this 'X' frequencies
            list_of_dics_counts[dic_num] = sum_of_freqs
            # increase number of dictionaries
            dic_num +=1
    #sort list of dictionaries count (sort X's descending) The most frequent
    list_of_dics_counts = dict(sorted(list_of_dics_counts.items(),key=operator.itemgetter(1),reverse=True))
    #new frequency dictionary that will return
    new_freq_dic =dict()
    #loop to make them as one dictionary after sorting
    for position in list_of_dics_counts.keys():
        new_sub_dic = dict(sorted(list_of_dics[position].items(),key=operator.itemgetter(1),reverse=True))
        for word,count in new_sub_dic.items():
            new_freq_dic[word] = count

    return new_freq_dic



def generate_latex_table(dictionary,filename,location="."):
    """generate latex code of table of frequency

    Args:
        dictionary: Dictionary, frequency dictionary
        filename: String, represents file name
        location: Optional, String, represents location to save , the default location is same directory
		
    Returns:
        Boolean: True if done, otherwise Flase

    Example:
    ```python
    frequency_dic = q.generate_frequency_dictionary(114)
    q.generate_latex_table(frequency_dic,'filename','../location')\n
    # it means done, the file 'filename.tex' is generated
	
    >>> True
    ```
    """
    if type(filename) != str:
        raise TypeError('filename should be string')
    if type(dictionary) != dict:
        raise TypeError('dictionary should be dictionary')

    head_code = """\\documentclass{article}
%In the preamble section include the arabtex and utf8 packages
\\usepackage{arabtex}
\\usepackage{utf8}
\\usepackage{longtable}
\\usepackage{color, colortbl}
\\usepackage{supertabular}
\\usepackage{multicol}
\\usepackage{geometry}
\\geometry{left=.1in, right=.1in, top=.1in, bottom=.1in}

\\begin{document}
\\begin{multicols}{6}
\\setcode{utf8}

\\begin{center}"""

    tail_code = """\\end{center}
\\end{multicols}
\\end{document}"""

    begin_table = """\\begin{tabular}{ P{2cm}  P{1cm}}
\\textbf{words}    & \\textbf{\\#}  \\\\
\\hline
\\\\[0.01cm]"""
    end_table= """\\end{tabular}"""
    rows_num = 40
    if location != '.':
         filename = location +"/"+ filename

    try:
        file  = open(filename+'.tex', 'w', encoding='utf8')
        file.write(head_code+'\n')
        n= int(len(dictionary)/rows_num)
        words = [("\\<"+word+"> & "+str(frequancy)+' \\\\ \n') for word, frequancy in dictionary.items()]
        start=0
        end=rows_num
        new_words = []
        for i in range(n):
            new_words = new_words+ [begin_table+'\n'] +words[start:end] +[end_table+" \n"]
            start=end
            end+=rows_num
        remain_words = len(dictionary) - rows_num*n
        if remain_words > 0:
            new_words +=  [begin_table+" \n"]+ words[-1*remain_words:]+[end_table+" \n"]
        for word in new_words:
            file.write(word)
        file.write(tail_code)
        file.close()
        return True
    except:
        return False


def shape(system):
    """shape declare a new system for alphabets ,user pass the alphabets "in a list of list"
	that want to count it as on shape "inner list" and returns a dictionary has the same value
	for each set of alphabets and diffrent values for the rest of alphabets

	Args:
		system: A list of list of alphabets , each inner list have
					  alphabets that with be count  as one shape .
	Returns:
		dict: Dictionary, with all alphabets, where each char "key"  have a value,
		values will be the alphabets that will be count as one shape
    
	Example:
	```python
	newSystem = [[q.beh, q.teh], [q.jeem, q.hah, q.khah]]
	updatedSystem = q.shape(newSystem)
	print(updatedSystem)\n
	
	>>> {'ب': 0, 'ت': 0, 'ث': 0, 'ج': 1, 'ح': 1, 'خ': 1, 'ء': 2, 'آ': 3, 'أ': 4, 'ؤ': 5, 'إ': 6, 'ئ': 7, 'ا': 8, 'ة': 9, 'د': 10, 'ذ': 11, 'ر': 12, 'ز': 13, 'س': 14, 'ش': 15, 'ص': 16, 'ض': 17, 'ط': 18, 'ظ': 19, 'ع': 20, 'غ': 21, 'ف': 22, 'ق': 23, 'ك': 24, 'ل': 25, 'م': 26, 'ن': 27, 'ه': 28, 'و': 29, 'ى': 30, 'ي': 31, ' ': 70}
	check_all_alphabet
	```
	"""
    newSys=system
    alphabetMap = OrderedDict()
    indx = 0

    newAlphabet = list(set(chain(*system)))
    theRestOfAlphabets = list(set(alphabet) - set(newAlphabet))

    for char in alphabet:
        if char in theRestOfAlphabets:
            alphabetMap.update({char: indx})
            indx = indx + 1
        elif char in newAlphabet:
            #sublist that contain this char(give all chars the same indx)
            #drop this sublist from the system
            systemItem = shapeHelper.searcher(newSys, char)
            for char in newSys[systemItem]:
                alphabetMap.update({char: indx})

            newSys=newSys[0:systemItem]+newSys[systemItem+1:]
            newAlphabet = list(set(chain(*newSys)))
            indx = indx + 1
    '''
    for setOfNewAlphabet in system:
        for char in setOfNewAlphabet:
            alphabetMap.update({char: indx})
        indx = indx + 1

    for char in theRestOfAlphabets:
        alphabetMap.update({char: indx})
        indx = indx + 1
    '''
    alphabetMap.update({" ": 70})
    return alphabetMap


def count_shape(text, system=None):
    """count_shape parses the text  and returns a N*P matrix (ndarray),
	the number of rows equals to the number of verses ,
	and the number of columns equals to the number of shapes.

	What it does:
		count the occuerence of each shape in text, depends on the your system ,
		If you don't pass system, then it will count each char as one shape.

		If `A` is a ndarray,
		then A[i,j] is the number of occurrences of alphabet(s)[j] in the
		verse i.

	Args:
		text: A list of strings , each inner list is ayah .
		system: Optional,
					- A list of list where each inner list has alphabets that will count as one shape
					- If you don't pass your system, it will count each char as one shape
	Returns:
		ndarray: with dimensions (N * P), where
		`N` is the number of verses in chapter and
		`P` the number of elements in system + the number of alphapets as on char [alphabets in system excluded]
		
	Example:
	```python
	newSystem=[[beh, teh, theh], [jeem, hah, khah]]
	alphabetAsOneShape =q.count_shape(get_sura(110), newSystem)
	print(alphabetAsOneShape)\n
	
	>>> [[1 2 1 0 0 0 1 0 4 0 0 1 1 0 0 0 1 0 0 0 0 0 1 0 0 3 0 1 1 1 0 0]
		 [1 2 0 0 2 0 0 0 5 0 2 0 1 0 1 0 0 0 0 0 0 0 2 0 0 4 0 3 1 3 1 3]
		 [6 2 0 0 0 0 1 0 4 0 1 0 2 0 2 0 0 0 0 0 0 1 2 0 2 0 1 2 2 2 0 0]]
	```
	"""

    #"there are a intersection between subsets"
    if system == None:
        alphabetMap = dict()

        indx = 0
        for char in alphabet:
            alphabetMap.update({char: indx})
            indx = indx + 1
        alphabetMap.update({" ": 70})
        p=len(alphabet)#+1 #the last one for space char

    else:
        for subSys in system:
            if not isinstance(subSys, list):
                raise ValueError ("system must be list of list not list")
        if shapeHelper.check_repetation(system):
            raise ValueError("there are a repetation in your system")

        p = len(alphabet) - len(list(set(chain(*system)))) + len(system)
        alphabetMap = shape(system)
    n=len(text)
    A=numpy.zeros((n, p), dtype=numpy.int)
    i=0
    j=0
    charCount =[]
    for verse in text:
        verse=shapeHelper.convert_text_to_numbers(verse, alphabetMap)
        for k in range(0,p,1) :
            charCount.insert(j, verse.count(k))
            j+=1
        A[i, :] =charCount
        i+=1
        charCount=[]
        j=0

    return A


def get_verse_count(surah):
    """counts the number of verses in surah

	Args:
		surah: String, represents a surah

	Returns:
		int: the number of verses
    
	Example:
    ```python
       numberOfAyat = pd.get_verse_count(q.get_sura(110,True))
	   print(numberOfAyat)\n
	   
	   >>> 3
    ```
	"""
    return len(surah)


def count_token(text):
    """counts the number of tokens that text (surah or ayah) has.

	Args:
		text: String or list of strings

	Returns:
		int: the number of tokens
    
	Example:
    ```python
       numberOfToken=q.count_token(q.tools.get_sura(110))
	   print(numberOfToken)\n
	   
	   >>> 19
    ```
	"""
    count=0
    if isinstance(text, list):
        for ayah in text:
            count=count+ayah.count(' ')+1
    else:
           count=text.count(' ')+1

    return count



def grouping_letter_diacritics(sentance):
    """Grouping each letter with its diacritics.

	Args:
		sentance: String, represents a sentance

	Returns:
		[str]: a list of _x_, where _x_ is the letter accompanied with its
		diacritics.

    Example:
    ```python
    q.separate_token_with_dicrites('إِنَّا أَعْطَيْنَكَ الْكَوْثَرَ')\n
	
    >>> ['إِ', 'نَّ', 'ا', ' ', 'أَ', 'عْ', 'طَ', 'يْ', 'نَ', 'كَ', ' ', 'ا', 'لْ', 'كَ', 'وْ', 'ثَ', 'رَ']
    ```
    """
    sentance_without_tatweel = strip_tatweel(sentance)
    print(sentance_without_tatweel)
    hroof_with_tashkeel = []
    for index,i in enumerate(sentance):
        if((sentance[index] in (alphabet or alefat or hamzat)or sentance[index] is ' ' )):
            k = index
            harf_with_taskeel =sentance[index]
            while((k+1) != len(sentance) and (sentance[k+1] in (tashkeel or harakat or shortharakat or tanwin ))):
                harf_with_taskeel =harf_with_taskeel+""+sentance[k+1]
                k = k + 1
            index = k
            hroof_with_tashkeel.append(harf_with_taskeel)
    return hroof_with_tashkeel



def frequency_of_character(characters,verse=None,chapterNum=0,verseNum=0 , with_tashkeel=False):
    """counts the number of characters occurrence,
        for specific verse, chapter or even all Quran.
        
	Args:
		verse: Optional, String, represents verse that needs to be counted it and default is None.
		chapterNum: Integer, chapter number is a number of 'sura'
					that will count it , and default is 0
		verseNum: Integer, verse number in sura
		chracters: List of characters that needs to be counted
		with_tashkeel: Boolean, to check if you want to search with tashkeel

	Returns:
		{dic}: {str : int} a dictionary and keys is a characters
				value is count of every chracter.
	
	Note:
		If you don't pass verse and chapterNum, it will get all Quran

				 
	Example:
	```python
	#count the verse number **2** in all swar
	q.frequency_of_character(['أ',"ب","تُ"],verseNum=2,with_tashkeel=False)\n
	
	>>> {'أ': 101, 'ب': 133, 'تُ': 0}

	#count the verse number **2** in chapter **1**
	q.frequency_of_character(['أ',"ب","تُ"],chapterNum=1,verseNum=2,with_tashkeel=False)\n
	
	>>> {'أ': 0, 'ب': 1, 'تُ': 0}

	#count in **all Quran**
	q.frequency_of_character(['أ',"ب","تُ"],chapterNum=1,verseNum=2,with_tashkeel=False)\n
	
	>>> {'أ': 8900, 'ب': 11491, 'تُ': 2149}

	```
    """
    if type(characters) != list:
        raise TypeError('characters should be list of characters')
    if type(chapterNum) != int:
        raise TypeError('chapterNum  should be integer')
    if type(verseNum) != int:
        raise TypeError('verseNum  should be integer')

    #dectionary that have frequency
    frequency = dict()
    #check if count specific verse
    if verse!=None:
        if type(verse) != str:
            raise TypeError('verse should be string')
        if not with_tashkeel:
            verse = strip_tashkeel(verse)
        #count frequency of chars
        frequency = searchHelper.hellper_frequency_of_chars_in_verse(verse,characters)

    #check if count specific chapter
    elif chapterNum!=0:
        if chapterNum <0 or chapterNum > arabic.swar_num:
            raise ValueError('chapterNum should be integer number in range [1-114]')
        #check if count specific verse in this chapter
        if verseNum!=0:
            #check if verseNum out of range
            if(verseNum<0):
                raise ValueError('chapterNum should be positive integer ')
            verse = quran.get_sura(chapterNum,with_tashkeel=with_tashkeel)[verseNum-1]
            #count frequency of chars
            frequency = searchHelper.hellper_frequency_of_chars_in_verse(verse,characters)
        else:
            #count on all chapter
            chapter = " ".join(quran.get_sura(chapterNum,with_tashkeel=with_tashkeel))
            #count frequency of chars
            frequency = searchHelper.hellper_frequency_of_chars_in_verse(chapter,characters)
    else:
        if verseNum!=0:
            if(verseNum<0):
                raise ValueError('chapterNum should be positive integer ')
            #count for specific verse in all Quran
            Quran = ""
            for i in range(swar_num):
                 Quran = Quran +" "+quran.get_verse(i+1,verseNum,with_tashkeel=with_tashkeel)+" "
            #count frequency of chars
            frequency = searchHelper.hellper_frequency_of_chars_in_verse(Quran,characters)
        else:
            #count for all Quran
            Quran = ""
            for i in range(swar_num):
                 Quran = Quran +" "+ " ".join(quran.get_sura(i+1,with_tashkeel=with_tashkeel))+" "
            #count frequency of chars
            frequency = searchHelper.hellper_frequency_of_chars_in_verse(Quran,characters)
    return frequency




def get_token(tokenNum,verseNum,chapterNum,with_tashkeel=False):
    """get token from specific verse from specific chapter
	
	Args:
		tokenNum: Integer, represents position of token
		verseNum: Integer, represents the number of verse
		chapterNum: Integer, represents number of chapter
		with_tashkeel: Optional, Boolean, to check whether you need to search with taskeel or not

	Returns:
		str:  String, represents a verse
    
	Example:
	```python
	q.get_token(tokenNum=4,verseNum=1,chapterNum=1,with_tashkeel=True)\n
	
	>>> 'الرَّحِيمِ'
	```
    """
    if type(tokenNum) != int:
        raise TypeError('tokenNum should be integer')
    if type(chapterNum) != int:
        raise TypeError('chapterNum  should be integer')
    if type(verseNum) != int:
        raise TypeError('verseNum  should be integer')

    if chapterNum < 0 or chapterNum > arabic.swar_num:
        raise ValueError('chapterNum should be integer number in range [1-114]')
    if tokenNum <= 0:
        raise ValueError('tokenNum should be positive integer numbers and > 0')
    if(verseNum<0):
        raise ValueError('chapterNum should be positive integer ')

    try:
        tokens = quran.get_sura(chapterNum,with_tashkeel)[verseNum-1].split()
        if tokenNum > len(tokens):
            return ""
        else:
            return tokens[tokenNum-1]
    except:
        return ""








def search_sequence(sequancesList,verse=None,chapterNum=0,verseNum=0,mode=3):
    """take list of sequances and return matched sequance,
	it search in verse, chapter or in the whole Quran ,
	it return for every match :
		1- matched sequance
		2- chapter number of occurrence
		3- token number if word and 0 if sentence

	Note :
		*if found verse != None it will use it en search .

		*if no verse and found chapterNum and verseNum it will
		use this verse and use it to search.

		*if no verse and no verseNum and found chapterNum it will
		search in chapter.

		*if no verse and no chapterNum and no verseNum it will
		search in All Quran.

	it has many modes:
		1- search with decorated sequance (with tashkeel),
		   and return matched sequance with decorates (with tashkil).

		2- search without decorated sequance (without tashkeel),
		   and return matched sequance without decorates (without tashkil).

		3- search without decorated sequance (without tashkeel),
		   and return matched sequance with decorates (with tashkil).


	Args:
		chapterNum: Integer, number of chapter where function search
		verseNum: Integer, number of verse wher function search
		sequancesList: List of sequances that needs to be matched
		mode: Optional, Integer, mode that needs to be uses and the default mode is 3

	Returns:
		dict() :  key is sequances and value is a list of matched_sequance
				  and their positions

	Example:
	```python
	# search in chapter = 1 only using mode 3 (default)
	q.search_sequence(sequancesList=['ملك يوم الدين'],chapterNum=1)\n
	#it will return 
	#{'sequance-1' : [ (matched_sequance , position , vers_num , chapter_num) , (....) ],
	# 'sequance-2' : [ (matched_sequance , position , vers_num , chapter_num) , (....) ] }
	# Note : position == 0 if sequance is a sentence and == word position if sequance is a word 
	
	>>> {'ملك يوم الدين': [('مَلِكِ يَوْمِ الدِّينِ', 0, 4, 1)]}

	# search in all Quran using mode 3 (default)
	q.search_sequence(sequancesList=['ملك يوم'])\n
	
	>>> {'ملك يوم': [('مَلِكِ يَوْمِ', 0, 4, 1),  ('الْمُلْكُ يَوْمَ', 0, 73, 6),  ('الْمُلْكُ يَوْمَئِذٍ', 0, 56, 22),  ('الْمُلْكُ يَوْمَئِذٍ', 0, 26, 25)]}
	```   
    """
    if type(sequancesList) != list:
        raise TypeError('sequancesList should to be list of strings')
    if type(verse) != str and verse != None:
        raise TypeError('verse should to be string')
    if type(chapterNum) != int:
        raise ValueError('chapterNum  should be integer')
    if type(verseNum) != int:
        raise ValueError('verseNum  should be integer')

    if chapterNum < 0 or chapterNum > arabic.swar_num:
        raise ValueError('chapterNum should be integer number in range [1-114]')
    if(verseNum<0):
        raise ValueError('verseNumr should be positive integer and > 0')
    if mode <= 0 or mode > 3:
        raise ValueError('mode should be positive integer numbers 1,2 or 3 only')


    final_dict = dict()
    #loop on all sequances
    for sequance in sequancesList:
        #check mode 1 (taskeel to tashkeel)
        if mode==1:
             final_dict[sequance] = searchHelper.hellper_pre_search_sequance(
                                    sequance=sequance,
                                    verse=verse,
                                    chapterNum=chapterNum,
                                    verseNum=verseNum,
                                    with_tashkeel=True)
        # chaeck mode 2 (without taskeel to without tashkeel)
        elif mode==2:
            final_dict[sequance] = searchHelper.hellper_pre_search_sequance(
                                   sequance=sequance,
                                   verse=verse,
                                   chapterNum=chapterNum,
                                   verseNum=verseNum,
                                   with_tashkeel=False)
        # chaeck mode 3 (without taskeel to with tashkeel)
        elif mode==3:
            sequance = strip_tashkeel(sequance)
            final_dict[sequance] = searchHelper.hellper_pre_search_sequance(
                                   sequance=sequance,
                                   verse=verse,
                                   chapterNum=chapterNum,
                                   verseNum=verseNum,
                                   with_tashkeel=True,
                                   mode3=True)
    return final_dict




def search_string_with_tashkeel(string, key):
    """
	Args:
		string: represents sentence where to search in
		key: taskeel pattern

	Return: (True, text that have that tashkeel pattern)
	  (Flase, '')

	Assumption:
		Searches tashkeel that is exciplitly included in string.
	
	Example:
	```python
	   sentence = 'صِفْ ذَاْ ثَنَاْ كَمْ جَاْدَ شَخْصٌ'
	   tashkeel_pattern = ar.fatha + ar.sukun
	   results = q.search_string_with_tashkeel(sentence,tashkeel_pattern)
	   print(results)\n
	   
	   >>> [(3, 5), (7, 9), (10, 12), (13, 15), (17, 19)]
	```	
    """

    error.is_string(string, 'You must pass an string.')

    # tashkeel pattern
    string_tashkeel_only = searchHelper.get_string_taskeel(string)

    # searching taskeel pattern
    results = []
    for m in re.finditer(key, string_tashkeel_only):

        spacesBeforeStart = \
            searchHelper.count_spaces_before_index(string_tashkeel_only, m.start())
        spacesBeforeEnd = \
            searchHelper.count_spaces_before_index(string_tashkeel_only, m.start())

        begin =  m.start() * 2 - spacesBeforeStart
        end   = m.end() * 2 - spacesBeforeEnd
        one_result = (m.start(), m.end())
        results.append(one_result)

    if results == []:
        return False, []
    else:
        return True, results


def buckwalter_transliteration(string, reverse=False):
   """Back and forth Arabic-Bauckwalter transliteration. 
   Revise [Buckwalter](https://en.wikipedia.org/wiki/Buckwalter_transliteration)

	Args:
		string: to be transliterated.
		reverse: Optional boolean. `False` transliterates from Arabic to
		Bauckwalter, `True` transliterates from Bauckwalter to Arabic.

	Returns:
		str: transliterated string.


    Example:
    ```python
    q.buckwalter_transliteration('إِنَّا أَعْطَيْنَكَ الْكَوْثَرَ')\n
	
    >>> <in~aA >aEoTayonaka Alokawovara
    ```
    """
   for key, value in buckwalter.buck2uni.items():
       if not reverse:
            string = string.replace(value, key)
       else:
            string = string.replace(key, value)
   return string


def get_tashkeel_binary(ayah):
    """Takes str or list(ayah or sub ayah) and maps it to zeros and ones,
	zeros for sukoon and char without diarictics
	and ones for char with harakat and tanwin
	
	Args:
		ayah: String or list, 

	Returns:
		str : zeros and ones for each token
	
	Example:
	```python
	pattern = q.get_tashkeel_binary('إِنَّا أَعْطَيْنَكَ الْكَوْثَرَ')
	print(pattern)\n
	>>> ('1010 101011 001011', ['ِ', 'ْ', 'َ', '', '', 'َ', 'ْ', 'َ', 'ْ', 'َ', 'َ', '', '', 'ْ', 'َ', 'ْ', 'َ', 'َ'])
	```
	"""
    marksDictionary = {'ْ': 0, '': 0, 'ُ': 1, 'َ': 1, 'ِ': 1, 'ّ': 1, 'ٌ': 1, 'ً': 1, 'ٍ': 1}
    charWithOutTashkeelOrSukun = ''
    tashkeelPatternList = []  # list of zeros and ones
    marksList = []

    # convert the List o to string without spaces
    ayahModified = ''.join(ayah.strip())
    tashkeelPatternStringWithSpace = ''

    # check is there a tatweel in ayah or not
    if(tatweel in ayahModified):
     ayahModified = strip_tatweel(ayahModified)

    # check whether exist alef_mad in ayah if exist unpack the alef mad
    if (alef_mad in ayahModified):
      ayahModified = unpack_alef_mad(ayahModified)


    # separate tashkeel from the ayah
    ayahOrAyatWithoutTashkeel, marks = separate(ayahModified)

    for mark in marks:
    #the pyarabic returns the char of marks without tashkeel with 'ـ' so if check about this mark if not exist
    #append in list harakat and zero or ones in tashkeel pattern list if yes append the marks and patterns
        if (mark != 'ـ'):
          marksList.append(mark)
          tashkeelPatternList.append(marksDictionary[mark])
        else:
          marksList.append(charWithOutTashkeelOrSukun)
          tashkeelPatternList.append(marksDictionary[charWithOutTashkeelOrSukun])

    # convert list of Tashkeel pattern to String for each token in ayah separate with another token with spce
    for posOfCharInAyah in range(0, len(ayahOrAyatWithoutTashkeel)):
        if ayahOrAyatWithoutTashkeel[posOfCharInAyah] == ' ' and tashkeelPatternList[posOfCharInAyah] == 0:
             tashkeelPatternStringWithSpace += ' '
        else:
             tashkeelPatternStringWithSpace += str(tashkeelPatternList[posOfCharInAyah])
    return tashkeelPatternStringWithSpace, marksList


def factor_alef_mad(sentance):
    """Factors alef_mad in a sentance into alef_hamza and alef and returns the sentance.

	Args:
		sentance: String or list.

	Returns:
		str: sentance having the alef_mad factored

	Example:
    ```python
    q.unpack_alef_mad('آ')\n
	
    >>> 'أْأَ'
    ```
    """
    ayahWithUnpackAlefMad = ''
    for charOfAyah in sentance:
        if charOfAyah != 'آ':
            ayahWithUnpackAlefMad += charOfAyah
        else:
            ayahWithUnpackAlefMad += 'أَ'
            ayahWithUnpackAlefMad += 'أْ'
    return ayahWithUnpackAlefMad




def check_all_alphabet(system):
    '''check_alphabet get a list of alphabets or system(list of lists of alphabets)
	and return the rest of arabic alphabets [alphabets in system excluded]
	-in case sytem equals all arabic alphabets, it will return empty list.
	
	What it does:
		return the rest of arabic alphabets that not included in system.

	Args:
		system: List or list of lists of characters.

	Returns:
		list: include all other arabic alphabet.
    
	
	Example:
    ```python
	   system = [[q.beh, q.teh], [q.jeem, q.hah, q.khah]]
	   rest = q.check_all_alphabet(system)
	   print(rest)\n
	   
	   >>> ['ء', 'آ', 'أ', 'ؤ', 'إ', 'ئ', 'ا', 'ة', 'ث', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ى', 'ي']
    ```
    '''

    if isinstance(system, list):
        system=list(chain(*system))
    theRestOfAlphabets = list(set(alphabet) - set(system))
    return theRestOfAlphabets


def check_system(system, index=None):
    """Returns the alphabet including treated-as-one letters.
    If you pass the index as the second optional arguement,
    it returns the letter of the that index only, not the hole alphabet.


	Args:
		system: [[char]],List of letters, where each letter to be treated as
		one letter are in one sub-list,  see  [Alphabetical Systems](#alphabetical-systems).
		index: Optional integer, is a index of a letter in the new system.

	Returns:
		list: full sorted system or a specific index.

    Example:
    ```python
    q.check_system([['alef', 'beh']])\n
	
    >>> [['ء'],
        ['آ'],
        ['أ', 'ب'],
        ['ؤ'],
        ['إ'],
        ['ئ'],
        ['ا'],
        ['ة'],
        ['ت'],
        ['ث'],
        ['ج'],
        ['ح'],
        ['خ'],
        ['د'],
        ['ذ'],
        ['ر'],
        ['ز'],
        ['س'],
        ['ش'],
        ['ص'],
        ['ض'],
        ['ط'],
        ['ظ'],
        ['ع'],
        ['غ'],
        ['ف'],
        ['ق'],
        ['ك'],
        ['ل'],
        ['م'],
        ['ن'],
        ['ه'],
        ['و'],
        ['ى'],
        ['ي']]
    ```
    The previous example prints each letter as one element in a new alphabet list,
    as you can see the two letters alef and beh are considered one letter.
    """
    if shapeHelper.check_repetation(system) == True:
        raise ValueError ("there is a repetition in your system")


    p = len(alphabet) - len(list(set(chain(*system)))) + len(system)

    systemDict = shape(system)
    fullSys = [[key for key, value in systemDict.items() if value == i] for i
               in range(p)]
    if index==None:
        return fullSys
    else:
        return fullSys[index]


def search_with_pattern(pattern,sentence=None,verseNum=None,chapterNum=None,threshold=1):
    '''this function use to search in 0's,1's pattern and
	return matched words from sentence pattern
	dependent on the ratio to adopt threshold.

	Args:
	pattern: String, 0's and 1's pattern that you need to search.
	sentence: Strin, Arabic string with tashkeel where
					function will search.
	verseNum: Integer, number of specific verse where
					will search.
	chapterNum: Integer, number of specific chapter
					 where will search.
	threshold: Float, threshold of similarity , if 1 it will
					  get the similar exactly, and if not it will
					  get dependant on threshold number.

	Cases:
		1- if pass **sentece** only or with another args
			it will search in sentece only.
		2- if not passed **sentence** , passed **verseNum** and **chapterNum**,
			it will search in this verseNum that exist in chapterNum only.
		3- if not passed **sentence**,**verseNum** and passed **chapterNum** only,
			it will search in this specific chapter only.
		4- if not pass any args it will search in **all Quran** (not recommended, take long time).

	Return:
	   [list] : it will return list that have matched word, or
				matched senteces and return empty list if not found.

	Note: it's takes time dependent on your threshold and size of chapter,
		  so it's not support to search on All-Quran becouse
		  it take very long time more than 11 min.

	Example:
	```python
	# it will search in chapter **1** only
	p.search_with_pattern("011101",chapterNum=1)\n
	
	>>> ['لِلَّهِ رَبِّ', 'الْعَلَمِينَ', 'أَنْعَمْتَ عَلَيْهِمْ', 'الْمَغْضُوبِ عَلَيْهِمْ']
	```
    '''
    if type(pattern) != str or len(pattern)!= (pattern.count('0')+pattern.count('1')):
        raise TypeError('pattern should to be string of 0\'s and 1\'s like \'011011010\'')
    if type(sentence) != str and sentence != None:
        raise TypeError('sentece should to be string')
    if type(chapterNum) != int and chapterNum != None:
        raise TypeError('chapterNum  should be integer')
    if type(verseNum) != int and verseNum != None:
        raise TypeError('verseNum  should be integer')

    if chapterNum < 0 or chapterNum > arabic.swar_num:
        raise ValueError('chapterNum should be integer number in range [1-114]')
    if(verseNum!=None and  verseNum<0):
        raise ValueError('verseNumr should be positive integer and > 0')

    if threshold > 1 or threshold < 0:
       raise ValueError('Threshold should be 0 <= Threshold <= 1')
    pattern = pattern.replace(' ','')
    if len(pattern)<=0:
        raise ValueError('pattern don\'t passed')

    #check if sentece exist
    if sentence != None:
        #convert sentence to 0/1
        sentence_pattern,taskieel = get_tashkeel_binary(sentence)
        return searchHelper.hellper_search_with_pattern(pattern=pattern,
                                           sentence_pattern=sentence_pattern,
                                           sentence=sentence,
                                           ratio=threshold)
    else:
        #check if search in specific chapter
        if chapterNum != None:
            #check if search in specific verese
            if verseNum != None:
                sentence = quran.get_verse(chapterNum=chapterNum,
                                     verseNum=verseNum,
                                     with_tashkeel=True)
            #search in all chapter
            else:
                sentence = " ".join(quran.get_sura(chapterNum,True))
        #search in all Quran
        else:
            raise ValueError('please send sentece or verseNum and chapterNum to search.')

        #convert sentence to 0/1
        sentence_pattern,taskieel = get_tashkeel_binary(sentence)
        sentence_pattern_without_spaces = sentence_pattern.replace(" ","")
        #check if no pattern exist
        if pattern not in sentence_pattern_without_spaces:
            return []
        else:
            return searchHelper.hellper_search_with_pattern(pattern=pattern,
                                               sentence_pattern=sentence_pattern,
                                               sentence=sentence,
                                               ratio=threshold)

def frequency_sura_level(suraNumber):
    """Computes the frequency dictionary for a sura

    Args:
        suraNumber: 1 <= Integer <= 114, the ordered number of sura in Mushaf.

    Return:
        [{word(str): word frequency(int)}]:
		A list of frequency dictionaries for each verse of Sura.

    Note:
        * frequency dictionary is a python dict, which carryies word frequences
          for an aya.
        * Its key is (str) word, its value is (int) word frequency
    
	Example
	```python
	
	```
	"""
    # A list of frequency dictionaries
    frequency_ayat_list = []
    for aya in quran.get_sura(suraNumber):
        frequency_ayat_list.append(get_frequency(aya))

    return frequency_ayat_list


def get_unique_words():
    """returns a set of all unique words in Quran

    TODO:
        need to support suras as well.
    """
    # Unique words
    words_set = set()
    for i in range(1, 114+1):
        sura  = quran.get_sura(i)
        for aya in sura:
            wordsList = aya.split(' ')
            for word in wordsList:
                words_set.add(word)

    return words_set


def get_words():
    """returns a list of all words in Quran

    TODO:
        need to support suras as well.
    """
    # words
    words_list = list()
    for i in range(1, 114+1):
        sura  = quran.get_sura(i)
        for aya in sura:
            wordsList = aya.split(' ')
            for word in wordsList:
                words_list.append(word)

    return words_list


def frequency_quran_level():
    """Compute the words frequences of the Quran.

    Returns:
        [sura_level_frequency_dict]: Revise the output of frequency_sura_level.

    Note:
        * quranWordsFrequences contains 114 sura_level_words_frequences.
        * Each sura_level_words_frequences contains frequency dictionary
            for every aya.

        In [19]: len(quran_words_frequences)
        Out[19]: 114

                 # Al Fati-ha
        In [20]: len(quran_words_frequences[0])
        Out[20]: 7
    """

    # * A list of sura level frequencies.
    # * Each element is a list of ayat el-sura frequencies.
    quranWordsFrequences = []

    for suraNumber in range(1, 114 +1):
        suraWordsFrequeces = frequency_sura_level(suraNumber)
        quranWordsFrequences.append(suraWordsFrequeces)

    return quranWordsFrequences


def prettify(elem):
    """Returns a pretty-printed XML string for the Element.
    """
    rough_string = etree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def quran_words_frequences_data(fileName):
    """Generates the entire words frequences of Quran into XML or JSON
	
	Args:
		fileName: The file where data will be written.
		
    ToDo:
        Sould support JSONs as well.
    """

    # Computing unique words
    unique_words = get_unique_words()
    comma_separated_unique_words = ''
    for word in unique_words:
        comma_separated_unique_words += word + ','

    # Removing the extra commas
    comma_separated_unique_words = comma_separated_unique_words.strip(',')



    # * Creating quran_words_frequences_data -- the root tag
    root = Element('quran_words_frequences')
    root.set('unique_words', comma_separated_unique_words)

    # * Add root to the tree
    tree = ElementTree(root)


    for suraNumber in range(1, 114 +1):

        sura = quran.get_sura(suraNumber)

        # * Creating sura Tag
        suraTag = Element('sura')

        # * set number attribute
        suraTag.set('number', str(suraNumber))

        # * set sura unique words
        # ??? update get_unique_words
        # suraTag.set('sura_unique_words', suraUniquewords)

        ayaCounter = 1
        for aya in sura:

            # Create aya Tag
            ayaTag = Element('aya')
            ayaTag.set('number', str(ayaCounter))

            # * Computes the words frequency for aya
            ayaWordsDict = get_frequency(aya)

            words_comma_separated = ''
            occurrence_comma_separated = ''

            for word in ayaWordsDict:
                words_comma_separated += word + ','
                occurrence_comma_separated += str(ayaWordsDict[word]) + ','

            # * The same order
            words_comma_separated = words_comma_separated.strip(',')
            occurrence_comma_separated = occurrence_comma_separated.strip(',')

            # * Add words & frequencies attributes
            ayaTag.set('unique_words', words_comma_separated)
            ayaTag.set('unique_words_frequencies', occurrence_comma_separated)


            # * Add aya tag to sura tag
            suraTag.append(ayaTag)

            ayaCounter += 1

        # * add suraTag to the root
        root.append(suraTag)


    # print(prettify(root))

    file = open(fileName, 'w')
    file.write(prettify(root))
    file.close()