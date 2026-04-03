from django.shortcuts import render
from django.http import HttpResponse
from . import funcs
from . import agentinteract
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def home(request):
    word = funcs.pickword()
    request.session['word'] = word
    newletter = funcs.getnewletter()
    request.session['letters'] = newletter
    request.session['guesses'] = {}
    request.session['agentletters'] = newletter
    request.session['agentguesses'] = {}
    request.session['wins'] = ""
    agentenv = agentinteract.AgentInteract() #Use agentenv to create an initial state and color info
    request.session['state'] = agentenv.getcurrentstate()
    request.session['colordict'] = agentenv.getcolorlistsdicts()

    context = {"word": word}
    return render(request, 'menu.html', context)

@csrf_protect
def instructions(request):
    word = request.session['word']
    context = {"word": word}
    if request.method == 'POST':
        letters = request.session['letters']
        guesses = request.session['guesses']
        submit = request.POST.get("submit")
        guessedword = request.POST.get("guessedword")
        tries = request.POST.get("tries")
        
        context = {
            "word": word,
            "letters": letters,
            "guesses": guesses,
            "submit": submit,
            "guessedword": guessedword,
            "tries": tries
        }
        
    return render(request, 'instructions.html', context)

# Plays game
@csrf_protect
def game(request):
    request.session['gameversion'] = 'solo'
    word = request.session['word']
    letters = request.session['letters']
    guesses = request.session['guesses']
    currguess = funcs.initcurrguess()
    guessedword = ""
    tries = 6
    error = "False"
    submit = ""
    letter = ""
    back = ""
    checkword = ""
    print(word)

    if request.method == 'POST': 
        submit = request.POST.get("submit")
        guessedword = request.POST.get("guessedword")
        letter = request.POST.get("addletter")
        back = request.POST.get("back")
        tries = request.POST.get("tries")
        
        #We haven't entered any words in yet
        if (guessedword != None and len(guessedword) > 0):
            currguess = funcs.populatecurrguess(guessedword)
        if (submit == "" or submit == None or submit == "None"):
            if (guessedword == None):
                guessedword = ""

            if (letter != None and letter != "" and letter != "None"):
                #If we can add letters, add one
                if (len(guessedword) < 5):
                    guessedword = funcs.addcurrguess(guessedword, letter)

                currguess = funcs.populatecurrguess(guessedword)
            elif(back != None and back != "" and back != "None"):
                #If we can delete letters, delete one
                if (len(guessedword) > 0):
                    guessedword = funcs.delcurrguess(guessedword)

                currguess = funcs.populatecurrguess(guessedword)
            #Otherwise we just assume current guess is empty with all white squares
            
        elif (guessedword != None and funcs.checkword(guessedword.lower()) == False):
            currguess = funcs.populatecurrguess(guessedword)
            error = "True"
        else:
            checkword = guessedword
            tries = int(request.POST.get("tries"))
            values = funcs.getcolors(guessedword, word.upper(), letters)
            guesses[7 - tries] = values["colorlist"]
            request.session['letters'] = values['letters']
            tries -= 1
            if (tries > 0):
                guessedword = ""
                currguess = funcs.initcurrguess()
    print(f"tries = {tries}")
    remaining = [[0 for i in range(5) ] for j in range(int(tries) - 1)]
    if ((submit == "True") and (word == checkword.lower())):
        request.session['guesses'] = guesses
        request.session['win'] = "win"
        return results(request)
    elif(tries == 0):
        request.session['guesses'] = guesses
        request.session['win'] = "lose"
        return results(request)
    else:
        request.session['guesses'] = guesses
        context = {
            "word": word, 
            "tries": tries, 
            "guesses": guesses, 
            "error": error, 
            "guessedword": guessedword, 
            "currguess": currguess,
            "remaining": remaining,
            "letters": letters,
            "back": back,
            "submit": submit,
            "letter": letter
        }
        
        return render(request, 'game.html', context)

# Plays game
@csrf_protect
def dualplaygame(request):
    request.session['gameversion'] = 'with agent'
    word = request.session['word']
    letters = request.session['letters']
    guesses = request.session['guesses']
    currguess = funcs.initcurrguess()
    guessedword = ""
    tries = 6
    error = "False"
    submit = ""
    letter = ""
    back = ""
    checkword = ""
    print(word)

    agentguessedword = ""
    agentcheckedword = ""
    agentletters = request.session['agentletters']
    agentguesses = request.session['agentguesses']
    agentenv = agentinteract.AgentInteract() #Creates agent object
    state = request.session['state']
    colordict = request.session['colordict']
    agentcurrguess = funcs.initcurrguess()
    #Init agentenv with stored state and colordict
    agentenv.setcurrentstate(state)
    agentenv.setcolorlistsdicts(colordict)


    if request.method == 'POST': 
        submit = request.POST.get("submit")
        guessedword = request.POST.get("guessedword")
        letter = request.POST.get("addletter")
        back = request.POST.get("back")
        tries = request.POST.get("tries")
        
        #We haven't entered any words in yet
        if (guessedword != None and len(guessedword) > 0):
            currguess = funcs.populatecurrguess(guessedword)
        if (submit == "" or submit == None or submit == "None"):
            if (guessedword == None):
                guessedword = ""

            if (letter != None and letter != "" and letter != "None"):
                #If we can add letters, add one
                if (len(guessedword) < 5):
                    guessedword = funcs.addcurrguess(guessedword, letter)

                currguess = funcs.populatecurrguess(guessedword)
            elif(back != None and back != "" and back != "None"):
                #If we can delete letters, delete one
                if (len(guessedword) > 0):
                    guessedword = funcs.delcurrguess(guessedword)

                currguess = funcs.populatecurrguess(guessedword)
            #Otherwise we just assume current guess is empty with all white squares
            
        elif (guessedword != None and funcs.checkword(guessedword.lower()) == False):
            currguess = funcs.populatecurrguess(guessedword)
            error = "True"
        else:
            #Shared between agent and player
            tries = int(request.POST.get("tries"))

            #We pressed the submit button -> agent will finally make a move
            #Have the agent make a move
            agentguessedword = agentenv.getagentmove()
            agentcheckword = agentguessedword
            agentvalues = funcs.getcolors(agentguessedword.upper(), word.upper(), agentletters)
            agentguesses[7 - tries] = agentvalues["colorlist"]
            request.session['agentletters'] = agentvalues['letters']

            #Update the state after the agent makes a move and we get a response 
            agentenv.updatestate(word, agentguessedword, 6 - tries)
            request.session['state'] = agentenv.getcurrentstate()
            request.session['colordict'] = agentenv.getcolorlistsdicts()

            #For player
            checkword = guessedword
            values = funcs.getcolors(guessedword, word.upper(), letters)
            guesses[7 - tries] = values["colorlist"]
            request.session['letters'] = values['letters']


            tries -= 1
            if (tries > 0):
                guessedword = ""
                currguess = funcs.initcurrguess()
                agentguessedword = ""
                agentcurrguess = funcs.initcurrguess()
    remaining = [[0 for i in range(5) ] for j in range(int(tries) - 1)]
    #Hit end of game, get ready to reset things for next game
    if ((submit == "True" and error != "True") and ((word == checkword.lower()) or (word == agentcheckword.lower())) or (tries == 0)):
        agentenv.reset()
        request.session['state'] = agentenv.getcurrentstate()
        request.session['colordict'] = agentenv.getcolorlistsdicts()
        request.session['guesses'] = guesses

    #You find the word first
    if ((submit == "True" and error != "True") and (word == checkword.lower()) and (word != agentcheckword.lower())):
        request.session['win'] = "win"
        return results(request)
    #The agent finds the word first
    elif ((submit == "True" and error != "True") and (word != checkword.lower()) and (word == agentcheckword.lower())):
        request.session['win'] = "agent wins"
        return results(request)
    #Both of you find the word on the same turn
    elif ((submit == "True" and error != "True") and (word == checkword.lower()) and (word == agentcheckword.lower())):
        request.session['win'] = "tie"
        return results(request)
    #Both of you can't find the word within max turns
    elif(tries == 0):
        request.session['win'] = "both lose"
        return results(request)
    else:
        request.session['guesses'] = guesses
        request.session['agentguesses'] = agentguesses
        context = {
            "word": word, 
            "tries": tries, 
            "guesses": guesses, 
            "agentguesses": agentguesses,
            "error": error, 
            "guessedword": guessedword, 
            "currguess": currguess,
            "remaining": remaining,
            "agentguessedword": agentguessedword, 
            "agentcurrguess": agentcurrguess,
            "letters": letters,
            "agentletters": agentletters,
            "back": back,
            "submit": submit,
            "letter": letter
        }
        
        return render(request, 'dualgame.html', context)

# Make agent play game
@csrf_protect
def agentplaygame(request):
    request.session['gameversion'] = 'agent only'
    word = request.session['word']
    letters = request.session['agentletters']
    guesses = request.session['agentguesses']
    agentenv = agentinteract.AgentInteract() #Creates agent object
    state = request.session['state']
    colordict = request.session['colordict']
    currguess = funcs.initcurrguess()
    guessedword = ""
    tries = 6
    submit = ""
    letter = ""
    back = ""
    checkword = ""

    #Init agentenv with stored state and colordict
    agentenv.setcurrentstate(state)
    agentenv.setcolorlistsdicts(colordict)

    if request.method == 'POST': 
        submit = request.POST.get("submit")
        back = request.POST.get("back")
        tries = request.POST.get("tries")
        currentstate = agentenv.getcurrentstate()

        #We pressed the submit button -> agent will finally make a move
        if (submit != None and submit != ""):
            #Have the agent make a move
            guessedword = agentenv.getagentmove()
            checkword = guessedword

            tries = int(request.POST.get("tries"))
            values = funcs.getcolors(guessedword.upper(), word.upper(), letters)
            guesses[7 - tries] = values["colorlist"]

            request.session['agentletters'] = values['letters']
            #Update the state after the agent makes a move and we get a response 
            agentenv.updatestate(word, guessedword, 6 - tries)
            request.session['state'] = agentenv.getcurrentstate()
            request.session['colordict'] = agentenv.getcolorlistsdicts()

            tries -= 1
            if (tries > 0):
                guessedword = ""
                currguess = funcs.initcurrguess()
    
    remaining = [[0 for i in range(5) ] for j in range(int(tries) - 1)]
    if ((submit == "True") and (word == checkword.lower())):
        agentenv.reset()
        request.session['state'] = agentenv.getcurrentstate()
        request.session['colordict'] = agentenv.getcolorlistsdicts()
        request.session['win'] = "win"
        request.session['agentguesses'] = guesses
        return results(request)
    elif(tries == 0):
        agentenv.reset()
        request.session['state'] = agentenv.getcurrentstate()
        request.session['colordict'] = agentenv.getcolorlistsdicts()
        request.session['win'] = "lose"
        request.session['agentguesses'] = guesses
        return results(request)
    else:
        request.session['agentguesses'] = guesses
        context = {
            "word": word, 
            "tries": tries, 
            "guesses": guesses, 
            "guessedword": guessedword, 
            "currguess": currguess,
            "remaining": remaining,
            "letters": letters,
            "back": back,
            "submit": submit,
        }
        
        return render(request, 'agentgame.html', context)

# Displays results
def results(request):
    version = request.session['gameversion']
    win = request.session['win']
    oldword = request.session['word']
    word = funcs.pickword()
    oldguesses = request.session['guesses']
    oldagentguesses = request.session['agentguesses']
    request.session['word'] = word
    newletter =  funcs.getnewletter()
    request.session['letters'] = newletter
    request.session['guesses'] = {}
    request.session['agentletters'] = newletter
    request.session['agentguesses'] = {}
    request.session['wins'] = ""
    context = {"win": win, "word": word, "oldword": oldword, "oldguesses": oldguesses, "oldagentguesses": oldagentguesses, "version": version}
    return render(request, 'results.html', context)
        
