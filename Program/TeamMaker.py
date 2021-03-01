import numpy as np
import itertools
import json
import os
import time  # sleep() sekund pocakat, #clear klera
import random

# izbolsave ##########################
# dodaj edit team data
# dodaj se en dict z clasi da pol mas moznost optimize for dps  recimo pol gleda da majo dps mirage

######################################
# progam data

RoleList = ["solokite", "BT", "lamp", "hfb", "healscg", "cTank", "druid", "epi", "alaren", "bs", "plyon", "hk", "offchrono"]
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
    print("choose from: solokite, BT, lamp, hfb, healscg, cTank, druid, epi, alaren, bs, plyon, hk, offchrono")
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


def PickRandom(compositions, RelevantRoles, NumberOfRoles):
    RandomComp = compositions[random.randint(0, len(compositions) - 1)]  # picks random composition from list

    roles = [role for role in RelevantRoles] + ["DPS" for i in range(10 - NumberOfRoles)]
    Dict = {}
    for index, role in enumerate(roles):
        try:
            Dict[role].append(RandomComp[index])
        except:
            Dict[role] = [RandomComp[index]]

    return Dict

def MakeComp(perm, RelevantRoles, pylon=False):
    '''Create all possible compositions from list "RelevantRoles".
    Perm is calculated when the program starts and it is list of all permutations made from TeamData

    RelevantRoles: list of all required roles for the encounter. Spelling must match those in RoleList in program data.
    DO NOT INCLUDE DPS in the RelevantRoles'''

    clear()
    print("Calculating...")
    NumberOfRoles = len(RelevantRoles)

    for index, possiblecomp in enumerate(perm):
        for jdex, player in enumerate(possiblecomp):
            if jdex >= NumberOfRoles:
                continue  # try break ?
            elif RelevantRoles[jdex] not in RoleDict[player]:
                perm[index] = None  # isto k false ce klices bool
                continue

    # get rid of Nones
    perm = remove_none(perm.copy())

    # get rid of permutations of dps players
    for index, x in enumerate(perm):
        if x:
            for jdex, y in enumerate(perm[index + 1:]):
                if y:
                    if y[:NumberOfRoles] == x[:NumberOfRoles]:
                        perm[index + 1 + jdex] = None

    # get rid of permutations of pylon players
    if pylon:
        for index, x in enumerate(perm):
            if x:
                for jdex, y in enumerate(perm[index + 1:]):
                    if y:
                        if y[NumberOfRoles:] in list(itertools.permutations(x[NumberOfRoles:])):
                            perm[index + 1 + jdex] = None

    # get rid of Nones
    compositions = remove_none(perm)

    # printing
    clear()

    print("Found", len(compositions), "possible compositions. Save?")
    x = input("y/n: ")
    if x == "y":
        filename = input("enter file name: ")
        with open(str(filename) + ".txt", "w") as file:
            for role in RelevantRoles:
                file.write(str(role)+"\t")
            for i in range(10-NumberOfRoles):
                file.write("DPS" + "\t")
            file.write("\n______________________________________________________________________________\n\n")
            for i in compositions:
                for j in i:
                    file.write(str(j) + "\t")
                file.write("\n")
        print("Data successfully saved to {}.txt".format(filename))
        print("\n")
        time.sleep(3)

    # print out results
    clear()
    print("printing compositions:")
    print("ROLE ODRER:", [role for role in RelevantRoles] + ["DPS" for i in range(10 - NumberOfRoles)])
    for i in compositions:
        print(i)
    print("ROLE ORDER:", [role for role in RelevantRoles] + ["DPS" for i in range(10 - NumberOfRoles)])
    print("\n")

    # make radom comp pick
    pick = "y"
    while (pick == "y"):
        print("Randomly selected composition: ")
        Dict = PickRandom(compositions, RelevantRoles, NumberOfRoles)
        d1 = dict(list(Dict.items())[len(Dict) // 2:])
        d2 = dict(list(Dict.items())[:len(Dict) // 2])
        print("\t".join("{} > {}".format(k, v) for k, v in d2.items()))
        print("\t".join("{} > {}".format(k, v) for k, v in d1.items()))
        print("\nPick again?")
        pick = input("y/n: ")
    print("\n")
    input("Press Enter to return to Menu")


################################################################################
############################################################################
############# main UI

# check if there is already player data and load it
try:
    with open("TeamData.json", "r") as file:
        players, RoleDict = json.load(file)
except:
    input("It looks like this is your first time using this program. Press Enter to input team data")
    get_team_data()
    clear()

###### init
print("Initializing...")
permutacije = list(itertools.permutations(players))

clear()

while (1):  # i dont really know how to make a "menu" like loop so i improvise
    ###### Menu
    print("Menu:")
    print("Current possible commands are:\n")
    print("*premade compositions: standard, boonthief, w4, w6", "w7")  # will add dhuum when i add rr and kite and epi
    print("*Add your own composition: add")
    print("*Close the program: exit")
    print("*edit current team: edit")
    print("*Make a new team: new")
    print("\n")

    x = input("input: ")  # user select an option here
    clear()
    ###########################################possible options:
    if x == "exit":
        break

    elif x == "standard":
        MakeComp(permutacije.copy(), ["cTank", "druid", "bs", "alaren", "hfb"])
    elif x == "boonthief":
        MakeComp(permutacije.copy(), ["BT", "druid", "bs",  "alaren", "healscg"])
    elif x == "w4":
        MakeComp(permutacije.copy(), ["cTank", "druid", "bs", "alaren", "hfb", "hk"])
    elif x == "w6":
        print("there is multiple compositions available for this raid")
        print("press 1 for hfb variant OR press 2 for healscg + offchrono variant")
        x = input("1, 2: ")
        if x == "1":
            MakeComp(permutacije.copy(), ["solokite", "druid", "alaren", "hfb", "cTank", "lamp"])
        elif x == "2":
            MakeComp(permutacije.copy(), ["solokite", "druid", "alaren", "healscg", "cTank", "lamp", "offchrono"])
    elif x == "w7":
        MakeComp(permutacije.copy(), ["cTank", "druid", "bs", "alaren", "hfb", "pylon", "pylon", "pylon"], pylon=True)

    elif x == "new":
        get_team_data()
        print("Initializing...")
        permutacije = list(itertools.permutations(players))

        clear()
