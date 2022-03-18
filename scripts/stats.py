import tests.performance as performance

def main():
    stat = performance.AllPawnMoveStep()
    print("Pawn (1 Steps)", stat)
    stat = performance.AllPawnMoveStep(None,2)
    print("Pawn (2 Steps)", stat)
    stat = performance.KnightMoveStep()
    print("Knight", stat)
    stat = performance.RookMoveStep()
    print("Rook", stat)
    stat = performance.BishopMoveStep()
    print("Bishop", stat)
    stat = performance.QueenMoveStep()
    print("Queen", stat)
    stat = performance.KingMoveStep()
    print("King", stat)

    print("Deploy", sum(performance.deploy_stat)/len(performance.deploy_stat))
    pass