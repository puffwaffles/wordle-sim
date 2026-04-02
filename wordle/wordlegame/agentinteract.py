import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
np.bool8 = np.bool_
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

import os, os.path
import json
from . import agent#import agent
from . import funcs#import funcs

#Allows the agent to interact with the wordle game
class AgentInteract():
    def __init__(self):
        #Set up the agent 
        self.stateshape = (3, 6, 5, 26)
        self.actionsize = 2309
        self.ddqnagent = agent.DDQNagent(self.stateshape, self.actionsize)
        #Sets up observation dict to be used as state for agent
        self.observation = {}
        self.observation['state'] = np.zeros(self.stateshape, dtype = np.float32)
        self.observation['mask'] = np.ones((self.actionsize, 1), dtype = np.float32)

        #Used to keep track of collected info on green, orange and gray letters
        self.greenlist = [] #List of indices
        self.orangedict = {} #Dictionary with entries: letter -> index list, #count (how many orange ones we found)
        self.graydict = {} #Dictionary with entries: letter -> #count (how many there should be in the word)

        #Get the index2word dictionary
        index2wordfile = funcs.getjsonpath('index2word')
        self.index2word = {}
        with open(index2wordfile, "r") as file:
            self.index2word = json.load(file)

        #Get the trained model's qnetwork and load to the agent
        filedirectory = os.path.dirname(os.path.abspath(__file__))
        qnetworkfile = os.path.join(filedirectory, "model/")
        qnetworkfile += "small_ddqn_5000.pt" 
        self.ddqnagent.loadqnetwork(qnetworkfile)

    #Reset observations and tracked values
    def reset(self):
        self.observation = {}
        self.observation['state'] = np.zeros(self.stateshape, dtype = np.float32)
        self.observation['mask'] = np.ones((self.actionsize, 1), dtype = np.float32)
        self.greenlist = [] 
        self.orangedict = {}
        self.graydict = {}


    def checkinvalid(self, word, correctword):
        invalid = False
        #Assess if it has the green letters
        for greenind in self.greenlist:
            #Stop if we find it is missing a correct word
            if (word[greenind] != correctword[greenind]):
                invalid = True
                return invalid

        #Assess if it doesn't have the orange letters or if the letter is in a confirmed wrong spot
        for orangeletter in self.orangedict.keys():
            #If the number of occurrences of the letter is the less than the amount of orange ones we found, we know it is not it
            if (word.count(orangeletter) < self.orangedict[orangeletter]['count']):
                invalid = True
                return invalid
            #If the word has the same letter in a confirmed orange spot, we know that can not be it
            for orangeind in self.orangedict[orangeletter]['index list']:
                if (word[orangeind] == orangeletter):
                    invalid = True
                    return invalid

        #Assess if it has gray letters
        for grayletter in self.graydict.keys():
            #If there are more instances of the letter than the maximum count, this can not be the word
            if (word.count(grayletter) > self.graydict[grayletter]):
                invalid = True
                return invalid
        
        return invalid

    def updatemask(self, correctword):
        for i in range(self.actionsize):
            if (self.observation['mask'][i] == 1 and self.checkinvalid(self.index2word[str(i)]['word'], correctword)):
                self.observation['mask'][i] = 0

    #Convert state np values into a dict of lists
    def convertstateinfo(self):
        state = {}
        #State is (3, 6, 5, 26)
        for color in range(self.stateshape[0]):
            for attempt in range(self.stateshape[1]):
                if (attempt not in state.keys()):
                    state[attempt] = {}
                    state[attempt]['letters'] = [] #Letter by alphabet position i.e. 'a' = 0
                    state[attempt]['colors'] = [] #By color position i.e. green = 0
                for letter in range(self.stateshape[2]):
                    for alpha in range(self.stateshape[3]):
                        if (self.observation['state'][color][attempt][letter][alpha] == 1):
                            state[attempt]['letters'].append(alpha) 
                            state[attempt]['colors'].append(color)
        #State represented as a dict indexed by attempt
        #Each attempt contains a list of letters (by alphabetical position) and a list of colors (by color position in np array)
        
        return state


    #Retrieve state
    def getcurrentstate(self):
        jsonobservation = {
            'state': self.convertstateinfo(),
            'mask': self.observation['mask'].tolist()
        }
        return jsonobservation

    #Retrieve lists and dicts for the colors
    def getcolorlistsdicts(self):
        colordict = {
            "greenlist": self.greenlist,
            "orangedict": self.orangedict,
            "graydict": self.graydict
        }
        return colordict

    #Extract values from state from .views to update state (we changed the state representation to make it jsonable)
    def convertviewsstate(self, statedict):
        for attempt in statedict.keys():
            for letter in range(len(statedict[attempt]['letters'])):
                color = statedict[attempt]['colors'][letter]
                self.observation['state'][color][int(attempt)][letter][statedict[attempt]['letters'][letter]] = 1

    #Set state
    def setcurrentstate(self, state):
        self.convertviewsstate(state['state'])
        self.observation['mask'] = np.array(state['mask'])

    #Set lists and dicts for the colors
    def setcolorlistsdicts(self, colordict):
        self.greenlist = colordict['greenlist']
        self.orangedict = colordict['orangedict']
        self.graydict = colordict['graydict']

    #The guesses in views.py is a dictionary with dictionary values using integer keys indexed from 1-6 (tries)
    #For each try, it is associated with a list of string colors (with a 'colorlist' key)
    #The letters list contain the corresponding letters

    #Uses the games info from views.py to update the state for the agent to see
    def updatestate(self, correctword, guessedword, tries):
        #Store previous greens, oranges, and grays encountered
        prevgreenlist, prevorangedict, prevgraydict = self.greenlist, self.orangedict, self.graydict 

        #Record greens, oranges, and grays encountered during attempt
        attemptgreenlist, attemptorangedict, attemptgraydict = [], {}, {}

        correctletters = 0
        #leftover letters from correct word and indices of leftover letters from guessed word after green space sweep
        leftovercorrect, leftoverguessindex = [], []

        #Update letters and green letters in first pass
        for i in range(5):

            #If letter matches, update status and correct letter cout
            if (guessedword[i] == correctword[i]):
                #Update state to show green for letter
                self.observation['state'][0][tries][i][ord(guessedword[i]) - ord('a')] = 1
                #Track number of fully correct letters
                correctletters += 1

                #Add this correct letter to our attempts list
                attemptgreenlist.append(i)

            #If the letter doesn't match, mark as gray for now. 2nd passes will fill in oranges ones
            else:
                #Update state to show gray for letter
                self.observation['state'][2][tries][i][ord(guessedword[i]) - ord('a')] = 1
                #Add correct letter to correct leftover letters list
                leftovercorrect.append(correctword[i])
                #Add index of guess letter to guessed leftover letter indices list
                leftoverguessindex.append(i)

        #Set win condition if all 5 letters are correct. Then function finishes
        if (correctletters == 5):
            self.win, terminated = True, True
        #Otherwise perform 2nd pass with orange
        else:
            j = 0
            #Fill in orange spots in there are any
            while (j < len(leftoverguessindex)):
                compind = leftoverguessindex[j] #Index of letter in guess
                completter = guessedword[compind] #Letter
                #If leftover letters contain the letter in guess, mark index as orange
                if (completter in leftovercorrect):
                    #Remove letter. This denotes that subsequent instances of the letter are considered extraneous
                    leftovercorrect.remove(completter)
                    #Set orange if green is not set
                    if (self.observation['state'][0][tries][compind][ord(guessedword[compind]) - ord('a')] == 0):
                        #Update state to show orange for letter
                        self.observation['state'][1][tries][compind][ord(guessedword[compind]) - ord('a')] = 1
                    
                        #If it was originally gray, unset gray status
                        if (self.observation['state'][2][tries][compind][ord(guessedword[compind]) - ord('a')] == 1):
                            #Unset gray status
                            self.observation['state'][2][tries][compind][ord(guessedword[compind]) - ord('a')] = 0
                            
                        #Add an entry for the letter if it not in the attempted orange list
                        if (completter not in attemptorangedict.keys()):
                            attemptorangedict[completter] = {}
                            attemptorangedict[completter]['index list'] = []
                            attemptorangedict[completter]['count'] = 0

                            #Add index and count of this orange letter
                            attemptorangedict[completter]['index list'].append(compind)
                            attemptorangedict[completter]['count'] += 1

                #If it still gray, add the letter to the attempted gray list
                #Add entry for letter if it is not in the gray list (for masking purposes)
                elif (completter not in attemptgraydict.keys()):
                    attemptgraydict[completter] = 0
                    #Check how many instances we know should be in there. Once we hit gray, we know we exceeded the total amount in the word
                    confirmedletter = 0
                    #Check all green instances of the letter
                    for greenind in attemptgreenlist:
                        if (guessedword[greenind] == completter):
                            confirmedletter += 1
                    #Check all orange instances of the letter
                    if (completter in attemptorangedict.keys()):
                        confirmedletter += attemptorangedict[completter]['count']

                    #Update count of confirmed letter instances
                    attemptgraydict[completter] = confirmedletter

                j += 1

        #Find new correct letters
        newgreen = list(set(attemptgreenlist).difference(set(prevgreenlist)))
        #Add new green indices to prevgreenlist
        prevgreenlist.extend(newgreen)   

        #Find new semicorrect letters
        for key in attemptorangedict.keys():
            if (key not in prevorangedict.keys()):
                #Update prevorangedict with new entry
                prevorangedict[key] = {}
                prevorangedict[key]['index list'] = attemptorangedict[key]['index list']
                prevorangedict[key]['count'] = attemptorangedict[key]['count']
            elif (key in prevorangedict.keys()):
                neworange = list(set(attemptorangedict[key]['index list']).difference(prevorangedict[key]['index list']))
                #Update prevorangedict with new indices
                prevorangedict[key]['index list'].extend(neworange)
                #Update count if it increases
                prevorangedict[key]['count'] = max(prevorangedict[key]['count'], attemptorangedict[key]['count'])     

        #Add new grays to dict 
        for key in attemptgraydict.keys():
            #The amount should stay the same once we discover it
            if (key not in prevorangedict.keys()):
                #Update prevgraydict with new count value
                prevgraydict[key] = attemptgraydict[key]

        #Update greenlist, orangedict, and graylist
        self.greenlist, self.orangedict, self.graydict = prevgreenlist, prevorangedict, prevgraydict

        #Update mask for newly discovered info
        self.updatemask(correctword)

    #Prompt agent to pick an action given a state
    def getagentmove(self):
        state = self.observation
        action = self.ddqnagent.greedy(state)
        word = self.index2word[str(action)]['word']
        return word