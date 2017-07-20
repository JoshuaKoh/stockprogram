arr = []
state = "A"

def insert(thing):
    arr.append(thing)

def state(newOne):
    state = newOne

def printArr():
    for a in arr:
        print a

def printState():
    print state
