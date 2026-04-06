from django.shortcuts import redirect, render
from django.http import HttpResponse
from . import funcs
from . import agentinteract
import random
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def home(request):
    wordleword = "wordle"
    wordlelist = []
    colors = ['green', 'orange', 'gray']
    color = random.choices(colors, weights = [0.2, 0.3, 0.5], k = 6)
    for i in range(len(wordleword)):
        wordlelist.append([wordleword[i], color[i]])

    word = funcs.pickword()
    request.session['word'] = word
    tries = 6
    request.session['tries'] = tries
    newletter = funcs.getnewletter()
    request.session['letters'] = newletter
    request.session['guesses'] = {}
    request.session['agentletters'] = newletter
    request.session['agentguesses'] = {}
    request.session['wins'] = ""
    agentenv = agentinteract.AgentInteract() #Use agentenv to create an initial state and color info
    request.session['state'] = agentenv.getcurrentstate()
    request.session['colordict'] = agentenv.getcolorlistsdicts()

    context = {"word": word, "tries": tries, "wordlelist": wordlelist}
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
        origin = request.POST.get("origin")
        
        context = {
            "word": word,
            "letters": letters,
            "guesses": guesses,
            "submit": submit,
            "guessedword": guessedword,
            "tries": tries,
            "origin": origin
        }
        
    return render(request, 'instructions.html', context)

#Maintains page for helper tool for coming up with words
@csrf_protect
def helpertool(request):
    ruletype = ""
    reset = ""
    deleterule = ""
    add = ""
    letter = ""
    number = 0
    wordlist = []
    defaulttab = "Green"

    #Init greenrules, orangerules, and grayrules as empty list at the same time
    if ('greenrules' not in request.session or 'greenrulelist' not in request.session):
        request.session['greenrules'] = {}
        request.session['greenrulelist'] = {}
    if ('orangerules' not in request.session or 'orangerulelist' not in request.session):
        request.session['orangerules'] = {}
        request.session['orangerulelist'] = {}
    if ('grayrules' not in request.session or 'grayrulelist' not in request.session):
        request.session['grayrules'] = {}
        request.session['grayrulelist'] = {}
    if ('priorityrules' not in request.session or 'priorityrulelist' not in request.session):
        request.session['priorityrules'] = False
        request.session['priorityrulelist'] = []
    if ('uniquerules' not in request.session or 'uniquerulelist' not in request.session):
        request.session['uniquerules'] = 0
        request.session['uniquerulelist'] = []


    greenrules = request.session['greenrules']#each entry is letter -> word index list
    orangerules = request.session['orangerules']#each entry is letter -> wordindex list
    grayrules = request.session['grayrules']#each entry is letter -> maxoccurrences
    priorityrules = request.session['priorityrules']#entry is either false or negative
    uniquerules = request.session['uniquerules']#entry is an integer
    greenrulelist = request.session['greenrulelist']#each entry is (letter, wordindex) -> rule as string
    orangerulelist = request.session['orangerulelist']#each entry is (letter, wordindex) -> rule as string
    grayrulelist = request.session['grayrulelist']#each entry is letter -> (letter, maxoccurrences) -> rule as string
    priorityrulelist = request.session['priorityrulelist']#each entry is rule as string (Only has one max)
    uniquerulelist = request.session['uniquerulelist']#each entry is rule as string (Only has one max)

    if request.method == 'POST':
        reset = request.POST.get("reset")
        add = request.POST.get("add")
        deleterule = request.POST.get("delete")
        ruletype = request.POST.get("ruletype")
        letter = request.POST.get("letter")
        number = request.POST.get("number")
        if (request.POST.get("defaulttab") != None):
            defaulttab = request.POST.get("defaulttab")
        if (number != None):
            number = int(number)

        #Delete all rules
        if (reset == 'reset'):
            greenrules = {}
            orangerules = {}
            grayrules = {}
            greenrulelist = {}
            orangerulelist = {}
            grayrulelist = {}
        #Delete a rule based on index
        elif (deleterule == "delete"):
            match ruletype:
                case "Green":
                    if (letter in greenrules.keys()):
                        greenrules[letter].remove(number)
                    if (letter in greenrulelist.keys()):
                        greenrulelist[letter].pop(str(number))
                    if (len(greenrules[letter]) == 0):
                        greenrules.pop(letter)
                        greenrulelist.pop(letter)
                case "Orange":
                    if (letter in orangerules.keys()):
                        orangerules[letter].remove(number)
                    if (letter in orangerulelist.keys()):
                        orangerulelist[letter].pop(str(number))
                    if (len(orangerules[letter]) == 0):
                        orangerules.pop(letter)
                        orangerulelist.pop(letter)
                case "Blue":
                    priorityrules = False
                    if (len(priorityrulelist) > 0):
                        priorityrulelist.pop()
                case "Red":
                    uniquerules = 0
                    if (len(uniquerulelist) > 0):
                        uniquerulelist.pop()
                case _:
                    grayrules.pop(letter)
                    grayrulelist.pop(letter)
        #Add rule type
        elif(add == 'add'):
            match ruletype:
                case "Green":
                    if (letter not in greenrules.keys()):
                        greenrules[letter] = []
                        greenrulelist[letter] = {}
                    if (number not in greenrules[letter]):
                        greenrules[letter].append(number)
                    if (str(number) not in greenrulelist[letter] and int(number) not in greenrulelist[letter]):
                        greenrulelist[letter][number] = "Has letter " + letter + " at position " + str(number)
                case "Orange":
                    if (letter not in orangerules.keys()):
                        orangerules[letter] = []
                        orangerulelist[letter] = {}
                    if (number not in orangerules[letter]):
                        orangerules[letter].append(number)
                    if (str(number) not in orangerulelist[letter] and int(number) not in orangerulelist[letter]):
                        orangerulelist[letter][number] = "Has letter " + letter + ", but not at position " + str(number)
                case "Blue":
                    priorityrules = True
                    priorityrulelist = ["Is a word in the possible answers list"]
                case "Red":
                    uniquerules = int(number)
                    uniquerulelist = ["Has at least " + str(number) + " unique letter(s)"]
                case _:
                    grayrules[letter] = number
                    grayrulelist[letter] = ["Only has " + str(number) + " instance(s) of " + letter, number]

    #Retrieve valid words
    wordslist = funcs.getvalidwordslist(greenrules, orangerules, grayrules, uniquerules, priorityrules)

    #Update rules:
    request.session['greenrules'] = greenrules
    request.session['orangerules'] = orangerules
    request.session['grayrules'] = grayrules
    request.session['greenrulelist'] = greenrulelist
    request.session['orangerulelist'] = orangerulelist
    request.session['grayrulelist'] = grayrulelist
    request.session['priorityrules'] = priorityrules
    request.session['uniquerules'] = uniquerules
    request.session['priorityrulelist'] = priorityrulelist
    request.session['uniquerulelist'] = uniquerulelist

    context = {
        "defaulttab": defaulttab,
        "greenrulelist": greenrulelist,
        "orangerulelist": orangerulelist,
        "grayrulelist": grayrulelist,
        "uniquerulelist": uniquerulelist,
        "priorityrulelist": priorityrulelist,
        "wordslist": wordslist
    }
    return render(request, 'helper.html', context)


# Plays game
@csrf_protect
def game(request):
    request.session['gameversion'] = 'solo'
    word = request.session['word']
    letters = request.session['letters']
    guesses = request.session['guesses']
    currguess = funcs.initcurrguess()
    guessedword = ""
    tries = request.session['tries']
    error = "False"
    submit = ""
    letter = ""
    back = ""
    checkword = ""
    origin = "game"

    if request.method == 'POST': 
        submit = request.POST.get("submit")
        guessedword = request.POST.get("guessedword")
        letter = request.POST.get("addletter")
        back = request.POST.get("back")
        tries = request.POST.get("tries")
        origin = request.POST.get("origin")
        
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
            request.session['tries'] = tries
    remaining = [[0 for i in range(5) ] for j in range(int(tries) - 1)]
    #We won -> end game
    if ((submit == "True") and (word == checkword.lower())):
        request.session['guesses'] = guesses
        request.session['win'] = "win"
        return results(request)
    #We lost -> end game
    elif(tries == 0):
        request.session['guesses'] = guesses
        request.session['win'] = "lose"
        return results(request)
    #We submitted a word -> use get
    elif (submit == "True"):
        return redirect('game')
    #We did not submit a word yet
    else:
        #Unset submit so that we don't accidentally submit again if we refresh
        submit = False
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
            "letter": letter,
            "origin": origin
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
    tries = request.session['tries']
    error = "False"
    submit = ""
    letter = ""
    back = ""
    checkword = ""


    origin = "dualplaygame"

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
        origin = request.POST.get("origin")
        
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
            request.session['tries'] = tries
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
    #We submitted a word -> use get
    elif (submit == "True"):
        return redirect('dualgame')
    else:
        #Unset submit so that we don't accidentally submit again if we refresh
        submit = False
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
            "letter": letter,
            "origin": origin
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
    tries = request.session['tries']
    submit = ""
    letter = ""
    back = ""
    checkword = ""

    origin = "agentplaygame"

    #Init agentenv with stored state and colordict
    agentenv.setcurrentstate(state)
    agentenv.setcolorlistsdicts(colordict)

    if request.method == 'POST': 
        submit = request.POST.get("submit")
        back = request.POST.get("back")
        tries = request.POST.get("tries")
        currentstate = agentenv.getcurrentstate()
        origin = request.POST.get("origin")

        #We pressed the submit button -> agent will finally make a move
        if (submit == "True"):
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
            request.session['tries'] = tries
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
    #We submitted a word -> use get
    elif (submit == "True"):
        return redirect('agentgame')
    else:
        #Unset submit so that we don't accidentally submit again if we refresh
        submit = False
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
            "origin": origin
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
        
