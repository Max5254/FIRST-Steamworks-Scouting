import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime

####TBA AUTHENTICATION
#code taken from ThePythonAlliance
#https://github.com/MC42/the-python-alliance/blob/master/thepythonalliance.py
baseURL = 'http://www.thebluealliance.com/api/v2/'
header = {'X-TBA-App-Id': 'FRC5254:SteemworksScouting:beta'}  # Yay, version strings....

####GOOGLE SHEETS AUTHENTICATION
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)
gc = gspread.authorize(credentials)
# Open a worksheet from spreadsheet with one shot
sh = gc.open_by_key('1TK5EPKoCmDVEfQLJDpOGWFWEwVTH_NQ1BNkXioY7iXg')
worksheet = sh.worksheet('Match Schedule')

# with open("Test1.csv",'r') as dest_f:
#     data_iter = csv.reader(dest_f,
#                            delimiter = ',',
#                            quotechar = '"')
#     data = [data for data in data_iter]
# data_array = np.asarray(data, dtype=None)

#print(data_array)

myRequest = (baseURL + 'event/2016nyro/matches')
response = requests.get(myRequest, headers=header)
jsonified = response.json()


myRequest = (baseURL + 'event/2016nytv/matches')
response = requests.get(myRequest, headers=header)
data = response.json()

def getTeam(x, color, station):
    return str(data[x]["alliances"][color]["teams"][station - 1])[3:]

data_array = []

for x in range(0, len(data)):
    if((data[x]["comp_level"]) == "qm"):
        data_array.append([data[x]["match_number"],
                       getTeam(x,"blue",1),
                       getTeam(x, "blue", 2),
                       getTeam(x, "blue", 3),
                       getTeam(x, "red", 1),
                       getTeam(x, "red", 2),
                       getTeam(x, "red", 3)
                       ])

data_array= sorted(data_array, key=lambda x: x[0])
print(data_array)

columns = len(data_array[0])
rows = len(data_array)


#Clear worksheet
clear_range = worksheet.range("A2:G100")
for cell in clear_range:
    cell.value = ""
# Update in batch
worksheet.update_cells(clear_range)


# Select a range
characters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','T','U','V','W','X','Y','Z']
location = "A2:" + characters[columns - 1] + str(rows + 1)
cell_list = worksheet.range(location)

print(cell_list)

r = c = 0
for cell in cell_list:
    if(r > columns - 1):
        r = 0
        c+= 1
    cell.value = data_array[c][r]
    r += 1


# Update in batch
worksheet.update_cells(cell_list)

worksheet.update_acell('H2', datetime.datetime.now())



