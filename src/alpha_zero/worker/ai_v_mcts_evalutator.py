from logging import getLogger
import logging
from alpha_zero.config import Config, PlayWithHumanConfig
from alpha_zero.env.connect4_env import Connect4Env
from alpha_zero.player.ai_player import *
from alpha_zero.player.human import *
from alpha_zero.player.mcts import MCTSPlayer
from alpha_zero.lib.helpers import Timer
import datetime
logger = getLogger(__name__)
logger.setLevel(logging.INFO)
import time
import timeit
import os
import numpy as np
import random as rnd
from alpha_zero.lib.play_one_game import *
import collections
from alpha_zero.player.mcts import MCTSPlayer
from alpha_zero.player.ai_player import *
import uuid
def play_Games(game,MCTSPlayer,AIPlayer,ngames=1,printBoard=True) :
    #this demonstrates who you would play two players against each other.
    #offlineOpponent is where the opponent is loaded in a different process while training is occuring.
    global loadingOpponentLOCK

    global lossAverage
    totalgamesPlayed=0
    LargestWins=0
    smallestLoss=1e-9
    game.reset()
    MCTSPlayer.playing_as=3-AIPlayer.playing_as
    #tracker = SummaryTracker()
    #id = random.randrange(len(opponents))  # picks an existing opponent to
    #saveOppToOppList(AIPlayer, opponents[id])  # take the weights from opponents[i] and assign them to AI player. AIPlayer is the variable used to play with.
    print("Playing games")
    result = gameResults()
    t0=timeit.default_timer()

    for i in range(ngames) :  #play n games before reporting
        # alternate player position

        #print("AIPLAYER BEFORE" + str(AIPlayer.player)),
        MCTSPlayer.playing_as = AIPlayer.playing_as
        AIPlayer.playing_as = 3 - MCTSPlayer.playing_as

        game.reset()  #TODO: have the environment reset without creating a new object
        winner=playOneGame(game,AIPlayer,MCTSPlayer)
        totalgamesPlayed+=1

        if (printBoard):
            pass
            #print ("game %d: " % (i),)
            #print("AI Player is: P"+str(AIPlayer.player) +":",)
            #print(game)
        if winner == AIPlayer.player:
            #print("AIPLAYER wins:"+str(AIPlayer.player)),

            if (printBoard):
                print ("AIP" + str(AIPlayer.playing_as) + ",", end='', flush=True)
            result.p1wins += 1
        elif winner == MCTSPlayer.playing_as:
            #print("OPPONENT wins:"+str(opponent.player)),
            if (printBoard):


                print ("MCTSP" + str(MCTSPlayer.playing_as) + ",", end='', flush=True)
            result.p2wins += 1
        elif winner == 3:
            if (printBoard):
                print ("Stale_AIP"+ str(AIPlayer.playing_as)+',', end='', flush=True)
            result.stale += 1
        else :
            print (winner)
            assert False  #No winner. incorrect value
    print()


    t1 = timeit.default_timer()


    print(str(totalgamesPlayed)+". "+str(datetime.datetime.now().strftime('%H:%M:%S'))+" AI_Player( %s ) MCTSPlayer(%s)\t Games:%4d\t AIPlayer:%4d\t MCTSPlayer:%4d\t stale:%4d\t t=%0.2fs" % (
      AIPlayer.shortName,MCTSPlayer.shortName, result.p1wins + result.p2wins + result.stale, result.p1wins, result.p2wins,
    result.stale,
    t1 - t0) )
    #tracker.print_diff()

    """
    print('memory %s (kb)'%resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    gc.collect()
    objgraph.show_most_common_types()
    """
    return result
import json
import shutil
import contextlib
import csv
tempFolder = os.path.abspath('../../../temp')
resultsFolder=os.path.abspath('../../../results')

def play_Games(game,MCTSPlayer : MCTSPlayer,AIPlayer:Alpha_Zero_Player,ngames=30,printBoard=True) :
    #this demonstrates who you would play two players against each other.
    #offlineOpponent is where the opponent is loaded in a different process while training is occuring.
    global loadingOpponentLOCK

    global lossAverage
    LargestWins=0
    smallestLoss=1e-9
    activeOnce=False
    game.reset()
    #MCTSPlayer.playing_as=3-AIPlayer.playing_as
    #tracker = SummaryTracker()
    #id = random.randrange(len(opponents))  # picks an existing opponent to
    #saveOppToOppList(AIPlayer, opponents[id])  # take the weights from opponents[i] and assign them to AI player. AIPlayer is the variable used to play with.
    print("Playing games")
    result = gameResults()
    t0=timeit.default_timer()



    for i in range(ngames) :  #play n games before reporting

        # alternate player position
        MCTSPlayer.playing_as = AIPlayer.playing_as
        AIPlayer.playing_as = 3 - MCTSPlayer.playing_as


        moveNum=0
        game.winner=0
        game.reset()

        winner=playOneGame(game,AIPlayer,MCTSPlayer)

        if (printBoard):
            pass
            #print ("game %d: " % (i),)
            #print("AI Player is: P"+str(AIPlayer.playing_as) +":",)
            #print(game.render())
        if winner == AIPlayer.playing_as:
            #print("AIPLAYER wins:"+str(AIPlayer.player)),

            if (printBoard):
                print ("AIP" + str(AIPlayer.playing_as) + ",", end='', flush=True)
            result.p1wins += 1
        elif winner == MCTSPlayer.playing_as:
            #print("OPPONENT wins:"+str(opponent.player)),
            if (printBoard):


                print ("MCTSP" + str(MCTSPlayer.playing_as) + ",", end='', flush=True)
            result.p2wins += 1
        elif winner == 3:
            if (printBoard):
                print ("Stale_AIP"+ str(AIPlayer.playing_as)+',', end='', flush=True)
            result.stale += 1
        else :
            print (winner)
            assert False  #No winner. incorrect value
    print()


    t1 = timeit.default_timer()

    #AIPlayer.winsAverages.append([result.p1wins+result.stale,result.p2wins+result.stale][AIPlayer.player-1])
    #AIPlayer.winsAverages.append(result.p1wins + result.stale)

    #meanWins=np.mean(AIPlayer.winsAverages)
    #meanLoss=np.mean(AIPlayer.lossAverage)
    #newlowText=""
    #newhighText=""

    #if LargestWins<meanWins :
    #    LargestWins=meanWins
    #    newhighText="NEW HIGH"
    #elif LargestWins==meanWins :
    #    newhighText = "Equal HIGH"
    #if smallestLoss==0.0:
    #    pass

    #elif smallestLoss>meanLoss :
    #    newlowText= "NEW LOW"
    #    smallestLoss=meanLoss
    #elif smallestLoss==meanLoss :
    #    newlowText= "Equal LOW"
    meanLoss=[0.0,0.0]
    meanWins=[0.0,0.0]
    newlowText=""
    newhighText=""
    g=AIPlayer.stats['total_steps']
    print(str(g)+". "+str(datetime.datetime.now().strftime('%H:%M:%S'))+" AI_Player( %s ) MCTSPlayer(%s)\t Games:%4d\t AIPlayer:%4d\t MCTSPlayer:%4d\t stale:%4d\t t=%0.2fs" % (
      AIPlayer.shortName,MCTSPlayer.shortName, result.p1wins + result.p2wins + result.stale, result.p1wins, result.p2wins,
    result.stale,
    t1 - t0) )
    #tracker.print_diff()
    if activeOnce:
        pass
    else:
        if smallestLoss==0:
            smallestLoss=1e9
            LargestWins=0
        else :
            activeOnce=True
    #print(mem_top(3))
    """
    print('memory %s (kb)'%resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    gc.collect()
    objgraph.show_most_common_types()
    """
    return result

def GetResultvsAgent(config,game,ai_model_folder,iterations,ngames=30): #this analyses the weights
    #move the files we want to the temp dir. This is to speed up loading in case the dir is on a server
    try: #if the
        h=str(uuid.uuid4().hex)
        modelname = config.resource.model_name
        modelweightsname = config.resource.model_weights_name
        modlestatsname = config.resource.model_stats_name
        m=''.join((h,modelname))
        config_path =os.path.join(tempFolder, m) #the hash is in case a separate worker wants to play with the same agent at the same time. This prevents another worker removing this file first.
        weight_path =os.path.join(tempFolder, ''.join((h,modelweightsname)))
        stats_path =os.path.join(tempFolder, ''.join((h,modlestatsname)))

        shutil.copyfile(os.path.join(ai_model_folder,modelname),config_path)
        shutil.copyfile(os.path.join(ai_model_folder,modelweightsname),weight_path)
        shutil.copyfile(os.path.join(ai_model_folder,modlestatsname),stats_path)

    except : #If there is some error I just really want to not perform the check
        raise
        logging.error(f"line244, ai_vs_mcts_evaluator.py error with moving files from {folder} to {tempFolder}. skipping check")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config_path)
        with contextlib.suppress(FileNotFoundError):
            os.remove(weight_path)
        with contextlib.suppress(FileNotFoundError):
            os.remove(stats_path)
        return None

    alphaPlayer=Alpha_Zero_Player(config,game,2)
    val=alphaPlayer.load(config_path, weight_path,stats_path)
    if not val: return gameResults()

    mctsPlayer=MCTSPlayer(game,playing_as=2,iterations=iterations)

    result = play_Games(game, MCTSPlayer=mctsPlayer, AIPlayer=alphaPlayer, ngames=ngames)

    with contextlib.suppress(FileNotFoundError):
        os.remove(config_path)
    with contextlib.suppress(FileNotFoundError):
        os.remove(weight_path)
    with contextlib.suppress(FileNotFoundError):
        os.remove(stats_path)

    return result

def start(config: Config):

    PlayWithHumanConfig().update_play_config(config.play)
    env = Connect4Env()
    env.reset()
    complete={} #keeps track of which AI weights have been tested.
    iterations = [100,500,1000,5000]
    ngames = 30
    winRates=collections.deque(maxlen=10)  #holds the latest winrates so that when the average crosses a threshold the number of iterations increases.
    addTowinRates=True #This is used to control whether to add values to the winRates. e if we are not plying the latest file then dont update winRates

    iteration_level=0
    perfDict = {}  # TODO Save the performance dictionary so it can be reloaded anytime.

    os.makedirs(tempFolder, exist_ok=True)
    os.makedirs(resultsFolder, exist_ok=True)
    playLatestOnly=False
    while True :
        played = False  # flag indicates if a game was played - in case all files have been analysed.
        if  (np.average(winRates)>0.65) and (len(winRates) >= winRates.maxlen):
            print("increasing iterations")
            iteration_level+=1
            perfDict.clear()
            winRates.clear()
        if iteration_level>(len(iterations)-1) :
            print("Resetting the iterations to 0")
            iteration_level=0
            perfDict.clear()
        parsed=False
        key=None
        while not parsed:
            """
            model_dir
            history_best_dir
            history_other_dir
            modelname = config.resource.model_weights_name
            modelweightsname = config.resource.next_generation_model_weight_filename
            modlestatsname = config.resource.next_generation_model_stats_filename
            """
            #basefolders=[config.resource.history_best_dir,config.resource.history_other_dir]
            basefolders=[config.resource.history_best_dir] #TODO: decide if this should test best or all

            folders=[]
            for folder in basefolders:

                folders += [str(os.path.join(folder, x)) for x in os.listdir(folder) if
                            os.path.isdir(os.path.join(folder, x))]

            #now create a corresponding list for how many steps based on the stats file.
            folders=list(folders)
            parsed = True
        #print(rnd, type(rnd))
        if playLatestOnly:
            loadNewest=True
            folders.sort()
            if (len(winRates) < winRates.maxlen) and (winRates.maxlen<=len(folders)):
                m = min(winRates.maxlen, len(folders))
                print("getting latest " + str(m))
                folders = folders[-m:]
            else:
                hpl = folders[-1]
                key = hpl.split("_")[-1]

                if (key in perfDict):
                    hpl = rnd.choice(folder)
                    print("-----RND: " + str(hpl))
                    addTowinRates = False
                else:
                    addTowinRates = True
                    print("-----Latest: "+str(key))
                folder = [hpl]


        else:
            rnd.shuffle(folders)
            folders = folders[:5]  #truncate the list to first 5 and we'll assess these ones.
        for folder in folders:
            key = folder.split("_")[-1]
            if not (key in perfDict):
                played = True

                result=GetResultvsAgent(config,env,folder,iterations[iteration_level] ,ngames=ngames)
                perfDict[key] = [result.p1wins, result.p2wins, result.stale]
                if not ((result.p1wins + result.p2wins + result.stale) == 0):

                    val = [key, result.p1wins, result.p2wins, result.stale]
                    csvFile=os.path.join(resultsFolder,str(iterations[iteration_level])+'.csv')
                    print('appending to:' + csvFile)
                    try:
                        with open(csvFile, 'a',
                                  newline='') as f:
                            wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                            wr.writerow(val)
                    except:
                        print("***************ERROR WRITING CSV. " + csvFile + '/results/' + str(
                            iterations[iteration_level]) + '.csv' + " IS IT CLOSED IN EXCEL??  *****************")

                    if addTowinRates: #If there is not enough new files to test this will play a randome one - we don't want the random playout to influence the winrate of the agent, only the latest
                        winRates.append((result.p1wins + result.stale) / (result.p1wins + result.p2wins + result.stale))
                else:
                    print("ZERO games played")
                print("Iterations:" + str(iterations[iteration_level]) + ", winrate:" + str(np.average(winRates))+", latestGames:"+str(len(winRates)))
        if not played:
            print("game not played")
            time.sleep(10)
            played = False
                #now save these results
if __name__ == '__main__':
    config = Config(config_type="normal")

    start(config)

