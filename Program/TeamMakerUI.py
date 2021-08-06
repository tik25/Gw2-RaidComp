import itertools
import json
import os
import time  # sleep() sekund pocakat
import random
import PySimpleGUI as sg

sg.theme('Dark Blue 8')

# izbolsave ##########################
# dodaj edit team data
# dodaj se en dict z clasi da pol mas moznost optimize for dps  recimo pol gleda da majo dps mirage
# makecomp nardi Class Team k ga returna in potem lahko cekiras da je cim vec istih ludi na istem rolu k primerjas class atribute(roli) med sabo
# makecomp mora met keyword argument da generira dicte useh compov za lazje primernjanje v wingih pol
######################################
# progam data

RoleList = ["solokite", "BT", "lamp", "hfb", "qfb", "rr", "healscg", "cTank", "druid", "epi", "alaren", "bs", "plyon",
            "hk", "offchrono"]


# TEAM DATA >> file je dics keys so imena ekip    vals so pa playter pa role dict

###################################

def remove_none(List):
    '''removes all None objects from a list'''

    newlist = []
    for i in List:
        if i:
            newlist.append(i)
    return newlist


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


def SaveComp(event, values):
    keys = [str(role) + "_SPIN" for role in RoleList]
    try:
        keyvals = [int(values[x]) for x in keys]
        if sum(keyvals) > 10:
            sg.popup("Squad size is limited to 10 players!", title="Error")
    except:
        sg.popup("you thought you could crash me?!?!", "use numbers please, like a normal person", title="Error")
        return
    name = values["addcompname"]
    try:
        CustomCompositions[name]
        if sg.popup_yes_no("Composition with this name already exists. Do you want to overwrite it?",
                           title="Attention") == "No":
            return
    except:
        pass

    temp = []
    for index, role in enumerate(RoleList):
        for i in range(keyvals[index]):
            temp.append(role)
    CustomCompositions[name] = temp
    # save
    with open("Saves/CustomCompositions.json", "w") as file:
        json.dump(CustomCompositions, file)
    sg.popup_quick_message("Composition successfully saved to CustomCompositions.json", title="Success",
                           auto_close_duration=1.5,
                           background_color="green")


def SaveTeam(event, values, players, RoleDict):
    if values["addteamname"] == "":
        sg.popup("\tNo name??\t", title="Error")
        return True
    else:
        try:
            with open("Saves/ProgramData/MyTeams.json", "r") as file:
                TeamData = json.load(file)
        except:
            TeamData = {}

        name = values["addteamname"]
        if name in TeamData.keys():
            if sg.popup_yes_no("Composition with this name already exists. Do you want to overwrite it?",
                               title="Attention") == "No":
                return

        # save
        TeamData[name] = (players, RoleDict)
        with open("Saves/ProgramData/MyTeams.json", "w") as file:
            json.dump(TeamData, file)
        sg.popup_quick_message("Team successfully saved to MyTeams.json", title="Success", auto_close_duration=1.5,
                               background_color="green")
        return False


def MakeComp(perm, name, RelevantRoles, TeamData, window, pylon=False):
    '''Create all possible compositions from list "RelevantRoles".
    Perm is calculated when the program starts and it is list of all permutations made from TeamData
    Role Dict has players for keys and roles for vals
    RelevantRoles: list of all required roles for the encounter. Spelling must match those in RoleList in program data.
    DO NOT INCLUDE DPS in the RelevantRoles'''

    RoleDict = TeamData[name][1]

    window.FindElement('OUTPUT').Update('')
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
    window.FindElement('OUTPUT').Update('')  # cleara output
    if len(compositions) == 0:
        sg.popup("Uh Oh!\nlooks like your team cannot run this composition :(", title="Yikes!")
        return 0, 0, 0
    print("Found", len(compositions), "possible compositions. Save?")
    x = sg.popup_yes_no("Save to txt file?")
    if x == "Yes":
        filename = sg.popup_get_text("enter file name: ", title="Save")
        if filename != None:
            with open("Saves/" + str(filename) + ".txt", "w") as file:
                for role in RelevantRoles:
                    file.write(str(role) + "\t")
                for i in range(10 - NumberOfRoles):
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
    print("\nprinting compositions:")
    print("ROLE ODRER:", [role for role in RelevantRoles] + ["DPS" for i in range(10 - NumberOfRoles)])
    for i in compositions:
        print(i)
    print("ROLE ORDER:", [role for role in RelevantRoles] + ["DPS" for i in range(10 - NumberOfRoles)])
    print("\n")

    print("\n")
    print("Click \"Select Random\" for a random composition")
    return compositions, RelevantRoles, NumberOfRoles


def pick(compositions, RelevantRoles, NumberOfRoles):
    print("Randomly selected composition: ")
    Dict = PickRandom(compositions, RelevantRoles, NumberOfRoles)
    d1 = dict(list(Dict.items())[len(Dict) // 2:])
    d2 = dict(list(Dict.items())[:len(Dict) // 2])
    print("\t".join("{} > {}".format(k, v) for k, v in d2.items()))
    print("\t".join("{} > {}".format(k, v) for k, v in d1.items()))
    print("\n")


################################################################################
############################################################################
############# main
# cehck if saves dir exists and make one
try:
    os.mkdir('Saves')
except:
    pass

try:
    os.mkdir('Saves/ProgramData')
except:
    pass

# check if core compositions file is present
try:
    with open("Saves/ProgramData/Compositions.json", "r") as file:
        Compositions = json.load(file)
except:
    input("Error: Compositions.json file not found\nPress Enter to generate one now.")
    Compositions = {"standard": ["cTank", "druid", "bs", "alaren", "hfb"],
                    "boonthief": ["BT", "druid", "bs", "alaren", "healscg"],
                    "deimos": ["cTank", "druid", "bs", "alaren", "hfb", "hk"],
                    "sh": ["cTank", "cTank", "druid", "druid", "bs", "alaren", "epi"],
                    "qadim hfb": ["solokite", "druid", "alaren", "hfb", "cTank", "lamp"],
                    "qadim healscg": ["solokite", "druid", "alaren", "healscg", "cTank", "lamp", "offchrono"],
                    "qadim2": ["cTank", "druid", "bs", "alaren", "hfb", "pylon", "pylon", "pylon"],
                    "dhuum": ["cTank", "druid", "druid", "qfb", "bs", "rr", "rr"],
                    "largos": ["cTank", "cTank", "druid", "druid"]}
    with open("Saves/ProgramData/Compositions.json", "w") as file:
        json.dump(Compositions, file)

# check if there is any saved comps
try:
    with open("Saves/ProgramData/CustomCompositions.json", "r") as file:
        CustomCompositions = json.load(file)
except:
    CustomCompositions = {}
    with open("Saves/ProgramData/CustomCompositions.json", "w") as file:
        json.dump(CustomCompositions, file)

###### init
print("Initializing...")
time.sleep(1)
os.system("cls")
print("Ready")

# zapiski

notes = {
    "1": "Recommended compositions:\n*standard -> 'cTank', 'druid', 'bs', 'alaren', 'hfb'\n\nNotes:\n*Vale guardian requires at least 2 condition dps\n*Sabetha requres 2 dedicated cannon jumpers (13 and 24), usually done by bannerslave and another dps",
    "2": "Recommended compositions:\n*standard -> 'cTank', 'druid', 'bs', 'alaren', 'hfb'\n*boonthief (Matthias only) -> 'BT', 'druid', 'bs', 'alaren', 'healscg'\n\nNotes:\n*If you are having trouble with Matthias, use boonthief compsition",
    "3": "Recommended compositions:\n*standard -> 'cTank', 'druid', 'bs', 'alaren', 'hfb'\n\nNotes:\n*escort towers are done by the cTank",
    "4": "Recommended compositions:\n*deimos (hk stays dps untill last boss) -> 'cTank', 'druid', 'bs', 'alaren', 'hfb', 'hk'\n*boonthief (Mursaat Overseer only) -> 'BT', 'druid', 'bs', 'alaren', 'healscg'\n\nNotes:\n*Deimos is often tanked with hfb, letting the cTank play quicnkess dps",
    "5": "Recommended compositions:\n*sh (Soulles Horror only) -> 'cTank', 'cTank', 'druid', 'druid', 'bs', 'alaren', 'epi'\n*dhuum (Dhuum only) -> 'cTank', 'druid', 'druid', 'qfb', 'bs', 'rr', 'rr'\n\nNotes:\n*sh has one druid as designated golem pusher\n*dhuum has one druid as stack heal, the other can be swaped for any kiting role",
    "6": "Recommended compositions:\n*standard (Conjured Amalgamate only) -> 'cTank', 'druid', 'bs', 'alaren', 'hfb'\n*largos (split) -> 'cTank', 'cTank', 'druid', 'druid'\n*largos (portal) -> 'cTank', 'druid', 'alaren', 'hfb'\n*qadim (hfb) -> 'solokite', 'druid', 'alaren', 'hfb', 'cTank', 'lamp'\n*qadim (healscg) -> 'solokite', 'druid', 'alaren', 'healscg', 'cTank', 'lamp', 'offchrono'\n\nNotes:\n*use only power dps on Conjured Amalgamate\n*do not run bs on Twin Largos\n*best dps for Twin Largos is condition chrono\n*if you cant afford a sololamp use dps players instead\n*if you have a spellbraker you can skip stability pyre with 'winds of disenchantment'",
    "7": "Recommended compositions:\n*qadim2 (pylon stays dps untill last boss) -> 'cTank', 'druid', 'bs', 'alaren', 'hfb', 'pylon', 'pylon', 'pylon'\n*boonthief (Adina optionally) -> 'BT', 'druid', 'bs', 'alaren'\n\nNotes:\n*if you are struggling use healscgourge on Adina/Sabir"
}


################################################################################
############################################################################
#############
# --------------------------GUI

def WINDOW_EXAMPLE(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['E&xit', '&About']]]

    # Table Data
    data = [["John", 10], ["Jen", 5]]
    headings = ["Name", "Score"]

    input_layout = [[sg.Menu(menu_def, key='-MENU-')],
                    [sg.Text('Anything that requires user-input is in this tab!')],
                    [sg.Input(key='-INPUT-')],
                    [sg.Slider(orientation='h', key='-SKIDER-'),
                     sg.Image(data=sg.DEFAULT_BASE64_LOADING_GIF, enable_events=True, key='-GIF-IMAGE-'), ],
                    [sg.Checkbox('Checkbox', default=True, k='-CB-')],
                    [sg.Radio('Radio1', "RadioDemo", default=True, size=(10, 1), k='-R1-'),
                     sg.Radio('Radio2', "RadioDemo", default=True, size=(10, 1), k='-R2-')],
                    [sg.Combo(values=('Combo 1', 'Combo 2', 'Combo 3'), default_value='Combo 1', readonly=True,
                              k='-COMBO-'),
                     sg.OptionMenu(values=('Option 1', 'Option 2', 'Option 3'), k='-OPTION MENU-'), ],
                    [sg.Spin([i for i in range(1, 11)], initial_value=10, k='-SPIN-'), sg.Text('Spin')],
                    [sg.Multiline(
                        'Demo of a Multi-Line Text Element!\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nYou get the point.',
                        size=(45, 5), k='-MLINE-')],
                    [sg.Button('Button'), sg.Button('Popup'),
                     sg.Button(image_data=sg.DEFAULT_BASE64_ICON, key='-LOGO-')]]

    asthetic_layout = [[sg.T('Anything that you would use for asthetics is in this tab!')],
                       [sg.Image(data=sg.DEFAULT_BASE64_ICON, k='-IMAGE-')],
                       [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='-PROGRESS BAR-'),
                        sg.Button('Test Progress bar')]]

    logging_layout = [[sg.Text("Anything printed will display here!")], [sg.Output(size=(60, 15), font='Courier 8')]]

    graphing_layout = [[sg.Text("Anything you would use to graph will display here!")],
                       [sg.Graph((200, 200), (0, 0), (200, 200), background_color="black", key='-GRAPH-',
                                 enable_events=True)],
                       [sg.T('Click anywhere on graph to draw a circle')],
                       [sg.Table(values=data, headings=headings, max_col_width=25,
                                 background_color='black',
                                 auto_size_columns=True,
                                 display_row_numbers=True,
                                 justification='right',
                                 num_rows=2,
                                 alternating_row_color='black',
                                 key='-TABLE-',
                                 row_height=25)]]

    specalty_layout = [[sg.Text("Any \"special\" elements will display here!")],
                       [sg.Button("Open Folder")],
                       [sg.Button("Open File")]]

    theme_layout = [[sg.Text("See how elements look under different themes by choosing a different theme here!")],
                    [sg.Listbox(values=sg.theme_list(),
                                size=(20, 12),
                                key='-THEME LISTBOX-',
                                enable_events=True)],
                    [sg.Button("Set Theme")]]

    layout = [[sg.Text('Demo Of (Almost) All Elements', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE, k='-TEXT HEADING-', enable_events=True)]]
    layout += [[sg.TabGroup([[sg.Tab('Input Elements', input_layout),
                              sg.Tab('Asthetic Elements', asthetic_layout),
                              sg.Tab('Graphing', graphing_layout),
                              sg.Tab('Specialty', specalty_layout),
                              sg.Tab('Theming', theme_layout),
                              sg.Tab('Output', logging_layout)]], key='-TAB GROUP-')]]

    return sg.Window('Gw2-RaidComp Pug', layout)


def choose_static_window(theme, TeamData):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Static Commander', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event

    tempstring = ", ".join(Compositions.keys())

    layout2 = [[sg.Text("Choose one of your groups")],
               [sg.Listbox(values=list(TeamData.keys()), size=(20, 15), key="TEAM", enable_events=True,
                           select_mode="LISTBOX_SELECT_MODE_SINGLE"),
                sg.Output(size=(70, 15), key="OUTPUT_TEAM", echo_stdout_stderr=False)],
               [sg.HorizontalSeparator()]
               ]
    layout3 = [[sg.HorizontalSeparator()]]
    # se customly dodane
    layout4 = [[sg.Button(button_text="Back", key="Menu", size=(13, 2), button_color="orange"), sg.Text(" "),
                sg.Button(button_text="Delete", k="DeleteTeam", size=(13, 2), button_color="gray"), sg.Text(" "),
                sg.Button(button_text="Add", size=(13, 2), button_color="white"), sg.Text("\t\t "),
                sg.Button(button_text="Load", size=(13, 2), button_color="green")]
               ]

    layout += layout2 + layout3 + layout4

    return sg.Window('Gw2-RaidComp Static', layout, font=14)


def static_window(theme, name, encounter="None"):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Menu(menu_def)],
              [sg.Text(name, size=(44, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event

    layout2 = [[sg.Button(button_text="Select encounter", size=(13, 2), button_color="green")],
               [sg.Text("Showing compositions for: {}".format(encounter))],
               [sg.Output(size=(90, 30), key="OUTPUT", echo_stdout_stderr=False)],
               [sg.HorizontalSeparator()],
               [sg.Button(button_text="Back", key="Static Commander", size=(13, 2), button_color="orange"),
                sg.Text("\t\t\t"),
                sg.Button(button_text="Select Random", size=(13, 2), button_color="gray"),
                ]]

    layout += layout2

    return sg.Window(name + ' Static', layout, element_justification="center", font=14)


def encounter_window(theme):
    # dodej spodi se search by wing

    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]
    layout = [[sg.Menu(menu_def)]]

    layout2 = [[sg.Text("All Compositions:")],
               [sg.Listbox(values=list(Compositions.keys()) + list(CustomCompositions.keys()), size=(20, 12),
                           key="COMP_SELECT", enable_events=True,
                           select_mode="LISTBOX_SELECT_MODE_SINGLE")],
               [sg.HorizontalSeparator()]
               ]
    layout3 = [[sg.HorizontalSeparator()],
               [sg.Button(button_text="Back", k="Load", size=(13, 2), button_color="orange"),
                sg.Button(button_text="Select", size=(13, 2), button_color="green")]]

    layout += layout2 + layout3

    return sg.Window('Gw2-RaidComp Compositions', layout, element_justification="center", font=14)


def comp_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Compositions', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event

    tempstring = ", ".join(Compositions.keys())

    layout2 = [[sg.Text("Default Compositions:")],
               [sg.Listbox(values=list(Compositions.keys()), size=(20, 12), key="COMP_DEF", enable_events=True,
                           select_mode="LISTBOX_SELECT_MODE_SINGLE"),
                sg.Output(size=(55, 12), key="OUTPUT_DEF", echo_stdout_stderr=False)],
               [sg.HorizontalSeparator()]
               ]
    layout3 = [[sg.HorizontalSeparator()]]
    # se customly dodane
    layout4 = [[sg.Text("Custom Compositions:")],
               [sg.Listbox(values=list(CustomCompositions.keys()), size=(20, 12), key="COMP_CUSTOM", enable_events=True,
                           select_mode="LISTBOX_SELECT_MODE_SINGLE"), sg.Text("\t"),
                sg.Button(button_text="Add a custom composition", size=(13, 2), button_color="white"),
                sg.Button(button_text="Delete a custom composition", k="DeleteComp", size=(13, 2), button_color="gray"),
                sg.Button(button_text="Back", k="Menu", size=(13, 2), button_color="orange")]
               ]
    layout5 = [[sg.Text("Custom Compositions:")],
               [sg.Button(button_text="Add a custom composition", size=(13, 2), button_color="white"),
                sg.Button(button_text="Delete a custom composition", k="DeleteComp", size=(13, 2), button_color="gray"),
                sg.Button(button_text="Back", k="Menu", size=(13, 2), button_color="orange")]
               ]

    layout += layout2 + layout3
    if list(CustomCompositions.keys()) != []:
        layout += layout4
    else:
        layout += layout5

    return sg.Window('Gw2-RaidComp Compositions', layout, font=14)


def new_comp_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Text('Add new composition', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event

    layout2 = [[sg.Menu(menu_def)]]

    test1 = [sg.Spin([i for i in range(0, 11)], initial_value=0, k=str(role) + "_SPIN", size=(5, 20)) for role in
             RoleList]
    test2 = [sg.Text(role) for role in RoleList]
    test = [i for t1t2 in zip(test2, test1) for i in t1t2]
    test1 = test[:len(test) // 3]
    test2 = test[len(test) // 3:2 * len(test) // 3]
    test3 = test[2 * len(test) // 3:]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Text('Enter composition name:')],
                    [sg.Input(key='addcompname')],
                    [sg.HorizontalSeparator()],
                    [sg.HorizontalSeparator()],
                    [sg.Text('Select number of players for each role. The remaining will be filled with DPS')],

                    test1,
                    test2,
                    test3,

                    [sg.Button('Back', key='Compositions', size=(12, 2), button_color="orange"), sg.Text("\t\t"),
                     sg.Button('Save', size=(12, 2), button_color="green")]]

    layout += input_layout + layout2

    return sg.Window('Gw2-RaidComp Compositions', layout, element_justification="center", font=14)


def new_team_window(theme, x):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Menu(menu_def)]]

    test = [sg.Checkbox(role, k=str(role) + "_box") for role in RoleList]
    test1 = test[:len(test) // 3]
    test2 = test[len(test) // 3:2 * len(test) // 3]
    test3 = test[2 * len(test) // 3:]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Text('Enter player name: '), sg.Input(key='addplayername')],
                    [sg.HorizontalSeparator()],
                    [sg.HorizontalSeparator()],
                    [sg.Text('Select player roles. DPS role is automatically assumed')],

                    test1,
                    test2,
                    test3,

                    [sg.Button('Cancel', k="Menu", size=(12, 2), button_color="orange"), sg.Text("\t\t\t"),
                     sg.Button('Add player', size=(12, 2), button_color="green")]]

    layout += input_layout

    return sg.Window('Add Player ' + str(x) + "/10", layout, element_justification="center", font=14)


def new_team_window_last(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    layout = [[sg.Menu(menu_def)]]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Text('Enter team name: '), sg.Input(key='addteamname')],
                    [sg.Button('Save Team', size=(12, 2), button_color="green")]]

    layout += input_layout

    return sg.Window('Name your team!', layout, element_justification="center", font=14)


def menu_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Button(button_text="Compositions", size=(13, 2), button_color="white")],
                    [sg.HorizontalSeparator()],
                    [sg.Text('Choose mode:')],
                    [sg.Button(button_text="Pug Commander", size=(15, 3)), sg.Text("\t\t\t   "),
                     sg.Button(button_text="Static Commander", size=(15, 3))],
                    ]

    layout = [[sg.Text('MENU', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event
    layout += input_layout

    return sg.Window('Gw2-RaidComp Menu', layout, element_justification="center", font=14)


###pug windows
def pug_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Text('daring today are we?', size=(40, 5), justification="center")],
                    [sg.HorizontalSeparator()],
                    [sg.Button(button_text="1", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="2", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="3", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="4", size=(15, 3))],
                    [sg.Button(button_text="5", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="6", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="7", size=(15, 3)), sg.Text("\t"),
                     sg.Button(button_text="8?!?", key="8", size=(15, 3))],
                    ]

    layout = [[sg.Text('Choose wing:', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event
    layout += input_layout

    return sg.Window('Gw2-RaidComp Menu', layout, element_justification="center", font=14)


def zapiski_window(theme, wingnumber):
    sg.theme(theme)
    wingnames = {"1": 'Spirit Vale', "2": 'Salvation Pass', "3": 'Stronghold of the Faithful',
                 "4": 'Bastion of the Penitent', "5": 'Hall of Chains', "6": 'Mythwright Gambit',
                 "7": 'The Key of Ahdashim'}
    layout = [
        [sg.Text(wingnames[wingnumber], size=(30, 1), justification='center', font=("Helvetica", 24),
                 relief=sg.RELIEF_RIDGE)],
        [sg.Button("Show recommended compositions", key="Show recommended compositions{}".format(wingnumber))],
        # nared gumb za comon comps pa pol izpise pa zravn usazga copy lfg messg
        [sg.HorizontalSeparator()],
        [sg.Text('Players', size=(15, 1), justification='leftside', font=("Helvetica", 16)),
         sg.VerticalSeparator(),
         sg.Text('Player Roles', size=(15, 1), justification='center', font=("Helvetica", 16)),
         sg.VerticalSeparator(),
         sg.Text('Notes', size=(15, 1), justification='side', font=("Helvetica", 16))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3)),
         sg.Text('      '),
         sg.Multiline('', size=(30, 3))],
        [sg.HorizontalSeparator()],
        [sg.Button('Menu', key='Menu', size=(12, 2), button_color="orange"), sg.Text("\t\t"),
         sg.Button('Clear', key=wingnumber, size=(12, 2), button_color="white")]]

    return sg.Window('Commanding wing {}'.format(wingnumber), layout, size=(1000, 1000), element_justification="center",
                     font=14)


def lfg_generator_window(theme, wingnumber):
    sg.theme(theme)
    menu_def = [['&Application', ['&About', 'E&xit']]]

    input_layout = [[sg.Menu(menu_def)],
                    [sg.Text(notes[wingnumber])],
                    [sg.HorizontalSeparator()]
                    ]
    layout = [[sg.Text('Recommended comps:', size=(38, 1), justification='center', font=("Helvetica", 24),
                       relief=sg.RELIEF_RIDGE)]]  # k = event
    layout += input_layout

    return sg.Window('Gw2-RaidComp Menu', layout, element_justification="center", font=14)


###
theme = 'Dark Blue 8'


def main(resitev):
    window = menu_window(theme)
    Load = False
    # Event Loop
    while True:
        if resitev:
            event, values = window.read(timeout=100)
        resitev = True
        if Load:
            print("Initializing...  Please Wait")
            permutations = list(itertools.permutations(TeamData[name][0]))
            print("DONE")
            time.sleep(1)
            window.FindElement('OUTPUT').Update('')
            print("please select an encounter")
            Load = False

        # debug
        '''
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print("event={}\nvalues={}".format(event, values))
        '''

        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break
        elif event == 'About':
            sg.popup("Program by tik25", "Available at https://github.com/tik25/Gw2-RaidComp", title="About")

        elif event == 'Compositions':
            window.close()
            window = comp_window(theme)
        elif event == 'Static Commander':
            name = None
            # check if there is already player data and load it
            try:
                with open("Saves/ProgramData/MyTeams.json", "r") as file:
                    TeamData = json.load(file)
                window.close()
                window = choose_static_window(theme, TeamData)
            except:
                sg.popup_ok("It looks like you dont have any teams saved yet. Press Ok to input team data",
                            title="Attention")
                window.close()
                event = 'Add'
                resitev = False

        elif event == 'Pug Commander':
            window.close()
            window = pug_window(theme)


        elif event == 'Menu':
            name = None
            window.close()
            window = menu_window(theme)
        elif event == 'Select encounter':
            window.close()
            window = encounter_window(theme)

        elif event == 'Add a custom composition':
            window.close()
            window = new_comp_window(theme)

        # klik za izpiske v konzolo
        elif event == 'TEAM':
            name = values['TEAM'][0]
            print("name=", name)
            data = TeamData[name]  # list [playerji (list), player data(dict)]
            window.FindElement('OUTPUT_TEAM').Update('')
            print("players: " + ", ".join(data[0]))
            print("\nPlayer roles:")
            for player in data[1].keys():
                print(player + ": " + ", ".join(data[1][player]))

        elif event == "Load":
            if 'name' not in locals() or name == None:
                sg.popup("you must select a team first!", title="Error")
                continue
            window.close()
            window = static_window(theme, name)
            Load = True
        elif event == "Select":
            try:
                comp = values["COMP_SELECT"][0]
            except:
                sg.popup("Please select a composition", title="Error")
                continue
            window.close()
            window = static_window(theme, name, comp)
            event, values = window.read(timeout=100)
            if comp in CustomCompositions.keys():
                if "pylon" in CustomCompositions[comp]:
                    pylon = True
                else:
                    pylon = "false"
                compositions, RelevantRoles, NumberOfRoles = MakeComp(permutations.copy(), name,
                                                                      CustomCompositions[comp], TeamData, window,
                                                                      pylon=pylon)
            else:
                if "pylon" in Compositions[comp]:
                    pylon = True
                else:
                    pylon = "false"
                compositions, RelevantRoles, NumberOfRoles = MakeComp(permutations.copy(), name, Compositions[comp],
                                                                      TeamData, window, pylon=pylon)
        elif event == 'COMP_DEF':
            window.FindElement('OUTPUT_DEF').Update('')
            print(Compositions[values['COMP_DEF'][0]])
        elif event == 'COMP_CUSTOM':
            window.FindElement('OUTPUT_DEF').Update('')
            print(CustomCompositions[values['COMP_CUSTOM'][0]])
        elif event == 'Select Random':
            if "compositions" not in locals() or "RelevantRoles" not in locals() or "NumberOfRoles" not in locals() or (
            compositions, RelevantRoles, NumberOfRoles) == (0, 0, 0):
                sg.popup("Generate first, random later")
            else:
                pick(compositions, RelevantRoles, NumberOfRoles)

        elif event == 'Save':
            if values["addcompname"] == "":
                sg.popup("Please enter a valid name", title="Error")
            else:
                SaveComp(event, values)
        elif event == 'DeleteTeam':
            teamname = sg.popup_get_text("Team name: ")
            name = None
            if teamname:
                try:
                    TeamData[teamname]
                except:
                    sg.popup("Team \"{}\" does not exist!".format(teamname))
                    continue

                delete = sg.popup_yes_no("are you sure you want to delete {}?".format(teamname))
                if delete == "Yes":
                    TeamData.pop(teamname)
                    if TeamData == [] or TeamData == {}:
                        os.remove("Saves/ProgramData/MyTeams.json")
                        window.close()
                        window = menu_window(theme)
                        continue
                    else:
                        with open("Saves/ProgramData/MyTeams.json", "w") as file:
                            json.dump(TeamData, file)
                        sg.popup_quick_message("Team successfully deleted", title="Success", auto_close_duration=1.5,
                                               background_color="green")
            window.close()
            window = choose_static_window(theme, TeamData)

        elif event == 'DeleteComp':
            name = sg.popup_get_text("Composition name: ")
            if name:
                try:
                    CustomCompositions[name]
                except:
                    sg.popup("Composition \"{}\" does not exist!".format(name))
                    continue
                delete = sg.popup_yes_no("are you sure you want to delete {}?".format(name))
                if delete == "Yes":
                    CustomCompositions.pop(name)
                    with open("Saves/ProgramData/CustomCompositions.json", "w") as file:
                        json.dump(CustomCompositions, file)
                    sg.popup_quick_message("Composition successfully deleted", title="Success", auto_close_duration=1.5,
                                           background_color="green")
                time.sleep(0.8)
                window.close()
                window = comp_window(theme)
        elif event in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            if event == "8":
                sg.popup("Ha, jebaited")
            else:
                window.close()
                window = zapiski_window(theme, event)

        elif event[:-1] == "Show recommended compositions":
            window2 = lfg_generator_window(theme, event[-1:])
            window2.read(timeout=100)

        elif event == 'Save Team':
            temp = SaveTeam(event, values, players, RoleDict)
            if temp:
                window.close()
                window = new_team_window_last(theme)
            else:
                with open("Saves/ProgramData/MyTeams.json", "r") as file:
                    TeamData = json.load(file)
                window.close()
                window = choose_static_window(theme, TeamData)


        elif event == 'Add':
            resitev = True
            name = None
            players = []
            RoleDict = {}
            window.close()
            window = new_team_window(theme, 1)

        elif event == "Add player":
            pname = values["addplayername"]
            List = []
            keys = [str(role) + "_box" for role in RoleList]
            keys = [values[x] for x in keys]
            for index, role in enumerate(RoleList):
                if keys[index]:
                    List.append(str(role))
            players.append(pname)
            RoleDict[pname] = List
            print(players)
            if len(players) == 10:
                window.close()
                window = new_team_window_last(theme)  # kle se choosas name
            else:
                window.close()
                window = new_team_window(theme, len(players) + 1)

    window.close()
    exit(0)


main(True)

# dodej right click Clear tm k izpisuje compositione
