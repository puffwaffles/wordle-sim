import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
np.bool8 = np.bool_

#We only need to initialize the agent to be able to pick actions

#Convolutional network used for qnetwork and targetqnetwork
class Cnnetwork(nn.Module):
  def __init__(self, oshape, actionsize, hiddendim):
    super(Cnnetwork, self).__init__()
    self.oshape = oshape
    self.actionsize = actionsize
    self.cnn1 = nn.Conv2d(in_channels = 18, out_channels = 32, kernel_size = (1, 26)) 
    self.cnn2 = nn.Conv2d(in_channels = 32, out_channels = 64, kernel_size = (3, 1), padding = (1, 0))
    
    self.layer1 = nn.Linear(64 * self.oshape[2], hiddendim)
    self.layer2 = nn.Linear(hiddendim, self.actionsize)

  #States are originally numpy arrays of shape (3, 6, 5, 26) where 3 are the input channels 0-2 denoting green, orange, gray for letter status
  #6 is for the attempt number, 5 is for each letter, and 26 designates the one hot encoding for each letter

  def forward(self, x):
    #Convert state into tensor
    if not isinstance(x, torch.Tensor):
      x = torch.tensor(x, dtype = torch.float32)
    #Insert dimension of size 1 at dimension 0 if batch is 1 (3, 6, 5, 26) -> (1, 3, 6, 5, 26)
    if (x.dim() == 4): 
      x = x.unsqueeze(0)
    #x is shape (batchsize, 3, 6, 5, 26)
    #Merge 2nd and 3rd dimension to get (batchsize, 18, 5, 26)
    x = x.view(x.shape[0], self.oshape[0] * self.oshape[1], self.oshape[2], self.oshape[3]) 
    x = F.relu(self.cnn1(x)) #Now x is shape (batchsize, 32, 5, 1)
    x = F.relu(self.cnn2(x)) #Now x is shape (batchsize, 64, 5, 1)

    #Flatten x
    x = x.view(x.size(0), -1) #Now x is shape (batchsize, 64 * 5 * 1)
    x = self.layer1(x) #Now x is shape (batchsize, hidden dim)
    x = self.layer2(x) #Now x is shape (hidden dim, actionsize)

    return x

#DDQN agent for site
class DDQNagent():
    def __init__(self, statesize, actionsize):
        self.statesize = statesize
        self.actionsize = actionsize
        #Qnetwork and targetnetwork
        self.qnetwork = Cnnetwork(self.statesize, self.actionsize, 512)

    #Load existing agent qnetwork
    def loadqnetwork(self, loadqnetwork):
        self.qnetwork.load_state_dict(torch.load(loadqnetwork, weights_only = False, map_location=torch.device('cpu')))

    #Picks greedy action
    def greedy(self, state):
        #Grab the actual state from the state dictionary
        actualstate = state['state']

        #Acquire qvalues
        with torch.no_grad():
          #Agent is using cpu here
          qvalues = self.qnetwork(actualstate).detach().data.numpy().squeeze()
        
        #Mask actions that are illogical
        mask = np.squeeze(state['mask'], axis = -1)
        lowvalue = -1e9
        validqvalues = np.where(mask, qvalues, lowvalue)
        action = np.argmax(validqvalues)
        """"""
        #action = np.argmax(qvalues)
        return action