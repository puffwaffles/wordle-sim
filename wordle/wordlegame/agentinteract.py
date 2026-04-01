import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
np.bool8 = np.bool_
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

import os, os.path
import json
import * from agent.py
import * from funcs.py

#Allows the agent to interact with the wordle game
class AgentInteract():
    def __init__(self):
        #Set up the agent 
        self.stateshape = (3, 6, 5, 26)
        self.gridshape = (6, 5, 29)
        self.actionsize = 2309
        self.ddqnagent = agent.DDQNagent(stateshape, actionsize)
        #Sets up observation dict to be used as state for agent
        self.observation = {}
        self.observation['state'] = np.zeros(self.stateshape, dtype = np.float32)
        self.observation['grid'] = np.zeros(self.gridshape, dtype = np.float32)
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
        qnetworkfile += "small ddqn 5000.pt" 
        self.ddqnagent.loadqnetwork(qnetworkfile)

    def checkinvalid(self, word, correctword):
        invalid = True
        return invalid

    def updatemask(self, correctword):
        for i in range(self.actionsize):
            if (self.observation['mask'][i] == 1 and self.checkinvalid(self.index2word[i]['word'])):
                self.observation['mask'][i] = 0

    #The guesses in views.py is a dictionary with dictionary values using integer keys indexed from 1-6 (tries)
    #For each try, it is associated with a list of string colors (with a 'colorlist' key)
    #The letters list contain the corresponding letters

    #Uses the games info from views.py to update the state for the agent to see
    def updatestate(self, correctword, guesses, letters, tries):
        attemptgreenlist = []
        attemptorangedict = {}
        attemptgraydict = {}




    #Prompt agent to pick an action given a state
    def getagentmove(self, state):
        action = self.ddqnagent.greedy(state)
        word = self.index2word[action]['word']
        return word