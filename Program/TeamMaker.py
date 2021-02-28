import numpy as np
import itertools
import json
import os
import time  # sleep() sekund pocakat, #clear klera

# izbolsave ##########################
# dodaj edit team data
# dodaj se en dict z clasi da pol mas moznost optimize for dps  recimo pol gleda da majo dps mirage


######################################
# progam data
RoleList = ["solokite", "BT", "lamp", "hfb", "healscg", "ChronoTank", "druid", "epi", "alaren", "bs", "plyon", "hk"]
clear = lambda: os.system('cls')


###################################

def remove_none(list):
    '''removes all None objects from a list'''

    newlist = []
    for i in list:
        if i:
            newlist.append(i)
    return newlist


def get_team_data():
    '''saves data about the static team including player names and roles'''

    print("input player names\n")
    players = []

    # names
    for i in range(10):
        x = input("player #{} name: ".format(i + 1))
        players.append(x)

    # roles
    print(
        "input player roles, separated by a single space, for each role. Note that code assumes everyone has a dps role available\n")
    print("choose from: solokite, BT, lamp, hfb, healscg, ChronoTank, druid, epi, alaren, bs, plyon, hk")
    RoleDict = {}
    for i in players:
        x = input("{}: ".format(i))
        x = x.split(" ")
        RoleDict[i] = x

    with open("TeamData.json", "w") as file:
        json.dump((players, RoleDict), file)
    print("Team data successfully saved to TeamData.json")
    print("Press Enter to return to Menu")
    return 0


def wing6hfb(perm):
    '''Create w6 composition with hfb as offheal and wyvrn kite. requires list of all permutations made from TeamData'''

    clear()
    print("Calculating...")
    RelevantRoles = ["solokite", "druid", "alaren", "hfb", "ChronoTank", "lamp", "DPS"]
    for index, possiblecomp in enumerate(perm):
        for jdex, player in enumerate(possiblecomp):
            if jdex >= 6:
                continue
            elif RelevantRoles[jdex] not in RoleDict[player]:
                perm[index] = None  # isto k false ce klices bool
                continue

    # get rid of Nones
    perm = remove_none(perm.copy())

    # get rid of permutations of dps players
    for index, x in enumerate(perm):
        for y in perm[index + 1:]:
            if y:
                if y[:6] in list(itertools.permutations(x[:6])):
                    perm[index] = None
                    break

    # get rid of Nones
    compositions = remove_none(perm)

    # printing
    clear()

    print("Found", len(compositions), "possible compositions. Save?")
    x = input("y/n: ")
    if x == "y":
        filename = input("enter file name: ")
        with open(str(filename) + ".txt", "w") as file:
            file.write("solokite\tdruid\talaren\thfb\ttank\tlamp\tDPS\tDPS\tDPS\tDPS\n______________________________________________________________________________\n\n")
            for i in compositions:
                for j in i:
                    file.write(str(j) + "\t")
                file.write("\n")
        print("Data successfully saved to {}.txt".format(filename))
        print("\n")
        time.sleep(3)

    clear()
    print("printing compositions:\n (solokite, druid, alaren, hfb, tank, lamp, DPS, DPS, DPS, DPS)")
    for i in compositions:
        print(i)
    print("\n")
    input("Press Enter to return to Menu")


##################################################
# main UI
while (1):
    try:
        with open("TeamData.json", "r") as file:
            players, RoleDict = json.load(file)
    except:
        input("It looks like this is your first time using this program. Press Enter to input team data")
        get_team_data()
        clear()

    ###init
    print("Initializing...")
    permutacije = list(itertools.permutations(players))

    clear()
    ###
    print("this is a menu, options:ksoifjrs")  # opcije
    print("\n")

    x = input("input: ")
    clear()
    ###########################################opcije
    if x == "exit":
        break
    if x == "w6":
        print("there is multiple compositions available for this raid")
        print("press 1 for hfb variant OR press 2 for healscg + offchrono variant")
        x = input("1, 2: ")
        if x == "1":
            wing6hfb(permutacije.copy())
        elif x == "2":
            print("not yet implemented")
