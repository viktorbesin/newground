#script (python)

def main(prg):
    p = []
    p.append(("base",[]))
    p.append(("rules",[]))
    prg.ground(p)
    prg.solve()

#end.
