from collections import defaultdict


from src.Core.Galaxy import Galaxy

EXPLORETIMES = 1 # TODO complete comments
EXPLORETARGET = []
EXPLORELEVEL = 99

ATTACKTARGET = [[137,47,6]]
ATTACKTIMES = 1 #
ATTACKLEVEL = 20
#TODO customize fleet

attackTargetList=[]
exploretargetList=[]


def target2lst(TARGET,Lst):
    for i in TARGET:
        Lst.append(dict(zip(['galaxy','system','planet'],i)))



if __name__ == '__main__':

    target2lst(ATTACKTARGET,attackTargetList)
    target2lst(EXPLORETARGET,exploretargetList)
    tgtlevel=20
    task=defaultdict(int)
    task['attack']=1
    G=Galaxy('user','pass','server')
    G.getTasks(attackTargetList,(ATTACKLEVEL,ATTACKTIMES),exploretargetList,(EXPLORELEVEL,EXPLORETIMES),task)
    G.run()
