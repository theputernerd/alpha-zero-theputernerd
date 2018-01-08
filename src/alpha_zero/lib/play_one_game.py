#TODO: consider putting this funcitno in the library

class gameResults() :
    def __init__(self):
        self.p1wins=0
        self.p2wins=0
        self.stale=0

def playOneGame(env,p1,p2):
    p2.playing_as = 3 - p1.playing_as
    while not env.done:
        t = env.player_turn()
        if t == p1.playing_as:
            #with Timer() as t:
            action = p1.get_move(env.clone())
            #print(f"{action}({t.interval}s)", end='')

            #print(f"{p1.shortName} moves to: " + str(action))

        elif t == p2.playing_as:
            action = p2.get_move(env.clone())
            #print(f"{p2.shortName} move to: " + str(action))
        else:
            assert False  # turn doesn't match a player.
        env.step(action)
        #env.render()
    #print("\nEnd of the game.")
    #print("Game result:")
    #env.render()
    if env.winner == 1:
        return 1

    elif env.winner == 2:
        return 2
    elif env.winner == 3:
        return 3
    else:
        assert False#shouldnt be here.