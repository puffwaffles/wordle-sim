import json
import random
import os, os.path

def getjsonpath(file):
    filedirectory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(filedirectory, "jsons/")
    path += file + ".json"
    return path

def getcsvpath(file):
    filedirectory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(filedirectory, "csvs/")
    path += file + ".csv"
    return path

#Gets initialized letter list
def getnewletter():
    letfile = getjsonpath("letters")
    letdict = {}
    
    #Grab dictionary of words from json file
    with open(letfile, "r") as file:
        letdict = json.load(file)
    return letdict

#Finds row for given letter
def getletter(letter):
    row = ""
    letfile = getjsonpath("letters")
    letdict = {}
    letter = letter.upper()
    
    #Grab dictionary of words from json file
    with open(letfile, "r") as file:
        letdict = json.load(file)

    #Iterate through rows to find letter
    for rows, rowvalues in letdict.items():
        if (letter in rowvalues.keys()):
            row = rows

    return row

#Checks if word is valid
def checkword(word):
    valid = False
    if (len(word) == 5):
        #File for words
        wordfile = getjsonpath("words")
        worddict = {}
        
        #Grab dictionary of words from json file
        with open(wordfile, "r") as file:
            worddict = json.load(file)

        if (word in worddict.keys()):
            valid = True

    return valid

def pickword():
    #File for words
    wordfile = getjsonpath("words")
    worddict = {}
    word = ""
    
    #Grab dictionary of words from json file
    with open(wordfile, "r") as file:
        worddict = json.load(file)

    #Pick a random word from common word list
    commonlist = [key for key in worddict.keys() if worddict[key] == 1]
    size = len(commonlist)
    rand2 = random.randint(0, size)
    word = commonlist[rand2]
    
    return word

def initcurrguess():
    currguess = []
    for i in range(5):
        currguess.append([" ", "white"])
    return currguess

def addcurrguess(guessedword, letter):
    newguess = guessedword + letter
    return newguess

def delcurrguess(guessedword):
    newguess = guessedword[:-1]
    return newguess

def populatecurrguess(guessedword):
    currguess = initcurrguess()
    for i in range(len(guessedword)):
        currguess[i][0] = guessedword[i]
    return currguess


def getcolors(guess, word, letters):
    #dictionary of values
    values = {}
    #By default, assume all letters don't match 
    colorlist = []
    for i in range(5):
        colorlist.append([" ", "gray"])
    #New letters list
    newletters = letters
    #Leftover letters from word after green space sweep
    leftoverlet = []
    #Leftover letter indices from guess after green space sweep
    lettoverind = []
    #Fill in green spots
    for i in range(len(guess)):
        colorlist[i][0] = guess[i]
        if (guess[i] == word[i]):
            colorlist[i][1] = "green"
            newletters[getletter(guess[i])][guess[i]] = "green"
        else:
            #Add letters from word that did not match
            leftoverlet.append(word[i])
            #Add indices of letters from guess that did not match
            lettoverind.append(i)
            if (newletters[getletter(guess[i])][guess[i]] != "green"):
                newletters[getletter(guess[i])][guess[i]] = "gray"

    j = 0
    #Fill in orange spots in there are any. Orange if for letters in the wrong spot
    while(j < len(lettoverind)):
        #If leftover letters contain the word in guess, mark index as orange
        if (guess[lettoverind[j]] in leftoverlet):
            #Remove letter. This denotes that subsequent instances of the letter are considered extraneous
            leftoverlet.remove(guess[lettoverind[j]])
            colorlist[lettoverind[j]][1] = "orange"
            if (newletters[getletter(guess[lettoverind[j]])][guess[lettoverind[j]]] != "green"):
                newletters[getletter(guess[lettoverind[j]])][guess[lettoverind[j]]] = "orange"
        
        j += 1
    values["colorlist"] = colorlist 
    values['letters'] = newletters   
    return values

#Returns list of words that matches rules
def getvalidwordslist(greenrules, orangerules, grayrules, uniquerules, priorityrules):
    #File for words
    wordfile = getjsonpath("words")
    worddict = {}
    
    #Grab dictionary of words from json file
    with open(wordfile, "r") as file:
        worddict = json.load(file)

    wordslist = []
    
    #Iterate through word list to determine words that follow rules
    for words in worddict.keys():
        valid = True

        #Check priority 
        if (priorityrules == True and worddict[words] != 1):
            valid = False

        #Check unique rule
        if (valid == True):
            unique = []
            copies = 0
            for i in range(len(words)):
                if (words[i] not in unique):
                    unique.append(words[i])
                else:
                    copies += 1
                if (copies > len(words) - uniquerules):
                    valid = False
                    break

        #Check green rules
        if (valid == True):
            for key in greenrules.keys():
                if (words.count(key) < len(greenrules[key])):
                    valid = False
                    break
                for i2 in range(len(greenrules[key])):
                    if (words[greenrules[key][i2]] != key):
                        valid = False
                        break
                if (valid == False):
                    break
        
        #Check orange rules
        if (valid == True):
            for key in orangerules.keys():
                if (words.count(key) == 0):
                    valid = False
                    break
                for j2 in range(len(orangerules[key])):
                    if (words[orangerules[key][j2]] == key):
                        valid = False
                        break
                if (valid == False):
                    break


        #Check gray rules
        if (valid == True):
            for key in grayrules.keys():
                if (words.count(key) != grayrules[key]):
                    valid = False
                    break

        if (valid == True):
            wordslist.append(words)

    return wordslist

