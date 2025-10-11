from django.shortcuts import render
from django.http import HttpResponse
from . import funcs
from django.views.decorators.csrf import csrf_protect

# Create your views here.
def home(request):
    word = funcs.pickword()
    request.session['word'] = word
    request.session['letters'] = funcs.getnewletter()
    request.session['guesses'] = {}
    request.session['wins'] = ""
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
    
    if ((submit == "True") and (word == checkword.lower())):
        request.session['win'] = "win"
        return results(request)
    elif(tries == 0):
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
            "letters": letters,
            "back": back,
            "submit": submit,
            "letter": letter
        }
        
        return render(request, 'game.html', context)

# Displays results
def results(request):
    win = request.session['win']
    oldword = request.session['word']
    word = funcs.pickword()
    oldguesses = request.session['guesses']
    request.session['word'] = word
    request.session['letters'] = funcs.getnewletter()
    request.session['guesses'] = {}
    request.session['wins'] = ""
    context = {"win": win, "word": word, "oldword": oldword, "oldguesses": oldguesses}
    return render(request, 'results.html', context)
        
