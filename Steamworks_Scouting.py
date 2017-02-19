import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime
import pyimgur
from operator import itemgetter

####TBA AUTHENTICATION
#code taken from ThePythonAlliance
#https://github.com/MC42/the-python-alliance/blob/master/thepythonalliance.py
baseURL = 'http://www.thebluealliance.com/api/v2/'
header = {'X-TBA-App-Id': 'FRC5254:SteemworksScouting:beta'}

#imgur API
client_id = '553a684bfb74c46'
im = pyimgur.Imgur(client_id)
client_secret = 'a3c9db6724915332b454256493cbb0e854db1e5e'

####GOOGLE SHEETS AUTHENTICATION
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)
gc = gspread.authorize(credentials)
# Open a worksheet from spreadsheet with one shot
sh = gc.open_by_key('1TK5EPKoCmDVEfQLJDpOGWFWEwVTH_NQ1BNkXioY7iXg')
matchSchedule = sh.worksheet('Match Schedule')
allianceSheet = sh.worksheet('Elimination Matches')
rankSheet = sh.worksheet('FMS Rankings')
teamSheet = sh.worksheet('Team List')


##CONSTANTS
characters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','T','U','V','W','X','Y','Z']

##Code to pull from a csv into an array
# with open("Test1.csv",'r') as dest_f:
#     data_iter = csv.reader(dest_f,
#                            delimiter = ',',
#                            quotechar = '"')
#     data = [data for data in data_iter]
# data_array = np.asarray(data, dtype=None)
#print(data_array)
def getImage(teamNumber, year):
    imgURL = ""
    myRequest = (baseURL + 'team/frc' + str(teamNumber) + '/' + str(year) + "/media")
    response = requests.get(myRequest, headers=header)
    team = response.json()

    for x in range(0, len(team)):
        type = str(team[x]['type'])
        preferred = str(team[x]['preferred'])
        if (type == "imgur" and preferred == "True"):
            key = team[x]['foreign_key']
            image = im.get_image(key)
            imgURL = (image.link)
        elif (type == "cdphotothread" and preferred == "True"):
            key = team[x]['details']['image_partial']
            imgURL = "https://www.chiefdelphi.com/media/img/" + str(key)
    return imgURL

def getMatchSchedule(code):
    match_array = []
    myRequest = (baseURL + 'event/' + code + '/matches')
    response = requests.get(myRequest, headers=header)
    data = response.json()
    for x in range(0, len(data)):
        if((data[x]["comp_level"]) == "qm"):
            match_array.append([data[x]["match_number"],
                            str(data[x]["alliances"]["red"]["teams"][0])[3:],
                            str(data[x]["alliances"]["red"]["teams"][1])[3:],
                            str(data[x]["alliances"]["red"]["teams"][2])[3:],
                            str(data[x]["alliances"]["blue"]["teams"][0])[3:],
                            str(data[x]["alliances"]["blue"]["teams"][1])[3:],
                            str(data[x]["alliances"]["blue"]["teams"][2])[3:]
                           ])

    return sorted(match_array, key=lambda x: x[0])

def getTeamList(code):
    teamArray = []
    currentTeam = ""
    myRequest = (baseURL + 'event/' + code + '/teams')
    response = requests.get(myRequest, headers=header)
    teams = response.json()
    for x in range(0, len(teams)):
        currentTeam = str(teams[x]['team_number'])
        teamArray.append([int(currentTeam),
                          teams[x]['nickname'],
                          getImage(currentTeam, code[0:4])])

    teamArray.sort(key=itemgetter(0), reverse=False)
    return teamArray

def getAlliances(code):
    alliance_array = []
    myRequest = (baseURL + 'event/' + code)
    response = requests.get(myRequest, headers=header)
    alliances = response.json()
    if(alliances['alliances'] == []):
        return []
    for x in range(0, 8):
        alliance_array.append([str(alliances['alliances'][x]['picks'][0])[3:],
                               str(alliances['alliances'][x]['picks'][1])[3:],
                               str(alliances['alliances'][x]['picks'][2])[3:]])
    return alliance_array

def getRanks(code):
    myRequest = (baseURL + 'event/' + code + '/rankings')
    response = requests.get(myRequest, headers=header)
    ranks = response.json()

    ranksArray = []
    for x in range(0, len(ranks) - 1):
        ranksArray.append([ranks[x + 1][1], x+1 ])

    return ranksArray



#Clear worksheet
def clearWorksheet(wks, range):
    clear_range = wks.range(range)
    for cell in clear_range:
        cell.value = ""
    # Update in batch
    wks.update_cells(clear_range)


def outputToGoogleSheets(wks, arr, start):
    if (arr == []):
        return

    if (isinstance(arr[0], list)):
        columns = len(arr[0]) - 1
    else:
        columns = 0
    rows = len(arr) - 1
    #print(str(columns) + " " + str(rows))
    lowerVert = int(start[1:])
    lowerHorz = characters.index(start[0:1])
    #print(str(lowerHorz) + " " + str(lowerVert))
    location = start + ":" + characters[columns + int(lowerHorz)] + str(rows + lowerVert)
    #print(location)
    cl = wks.range(location)


    r = c = 0
    if (isinstance(arr[0], list)):
        for cell in cl:
            if(r > columns):
                r = 0
                c+= 1
            cell.value = arr[c][r]
            r += 1
    else:
        for cell in cl:
            cell.value = arr[r]
            r += 1

    # Update in batch
    wks.update_cells(cl)

eventCode = '2015nyro'

#Match Schedule
data_array = getMatchSchedule(eventCode)
clearWorksheet(matchSchedule, "A2:G100")
outputToGoogleSheets(matchSchedule, data_array, "A2")
matchSchedule.update_acell('L1', datetime.datetime.now())

#ranks
rank_array = getRanks(eventCode)
clearWorksheet(rankSheet,"A2:B100")
print(rank_array)
outputToGoogleSheets(rankSheet , rank_array, "A2" )

#Alliances
alliance_array = getAlliances(eventCode)
clearWorksheet(allianceSheet, "B3:E10")
outputToGoogleSheets(allianceSheet, alliance_array, "B3")

#team list
team_array = getTeamList(eventCode)
clearWorksheet(teamSheet, 'A2:C100')
outputToGoogleSheets(teamSheet, team_array , "A2")
