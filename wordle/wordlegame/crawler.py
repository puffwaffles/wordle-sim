import json
import requests
from bs4 import BeautifulSoup
import re

#Gets list of words used by wordle
def getwords():
    #File for words
    wordfile = "jsons/words.json"
    worddict = {}
    
    #Grab dictionary of words from json file
    with open(wordfile, "r") as file:
        worddict = json.load(file)

    url = "https://www.wordunscrambler.net/word-list/wordle-word-list"
    response = requests.get(url)
    if (response.status_code != 200):
        print("Error with url!")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        #Iterate through all wordle words to extract words
        for words in soup.find_all('li', attrs = {'class': re.compile(r"invert light")}):
            word = words.get_text().strip()
            #Update dictionary if word is not in it
            if (word not in worddict.keys()):   
                worddict[word] = 1
    
    #Write new data to file
    newdict = json.dumps(worddict, indent = 2)
    with open(wordfile, "w") as file:
        file.write(newdict)  

#Get allowed words for wordle
def getallowedwords():
    #File for words
    wordfile = "jsons/words.json"
    worddict = {}
    
    #Grab dictionary of words from json file
    with open(wordfile, "r") as file:
        worddict = json.load(file)

    url = "https://gist.github.com/dracos/dd0668f281e685bad51479e5acaadb93"
    response = requests.get(url)
    if (response.status_code != 200):
        print("Error with url!")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        #Iterate through all wordle words to extract words
        for words in soup.find_all('td', attrs = {'class': re.compile(r"blob-code blob-code-inner js-file-line")}):
            word = words.get_text().strip()
            #Update dictionary if word is not in it
            #Give lower priority since these words are more obscure
            if (word not in worddict.keys()): 
                print(f"Added {word} to the list!")  
                worddict[word] = 0

    #Sort worddict 
    worddict = dict(sorted(worddict.items()))

    #Write new data to file
    newdict = json.dumps(worddict, indent = 2)
    with open(wordfile, "w") as file:
        file.write(newdict)  

getwords()
getallowedwords()