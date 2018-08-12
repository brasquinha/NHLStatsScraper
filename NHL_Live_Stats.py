import requests #library for REST API calls
import json #library for JSON handling
import pandas

#find all the active team IDs 

rTeams = requests.get('https://statsapi.web.nhl.com/api/v1/teams')#gets response object
jTeams=json.loads(rTeams.text) #load response text as JSON object
json.dump(jTeams, open('allTeams.json', 'w')) #dump this to a file

jTeams['teams'][0]['id']

#debug
#print(jTeams)
#print(json.dumps(jTeams, indent=4, sort_keys=False))

#make list of active team IDs
teamIDList=[team['id'] for team in jTeams['teams']]
#debug
#	print(str(team['id'])+': '+team['name'])

#Pull all team roster IDs - eg, all active players this season
allRosterIDs=[]
for teamID in teamIDList:
	print('Loading team (ID='+str(teamID)+')')
	rThisTeam = requests.get('https://statsapi.web.nhl.com/api/v1/teams/'
		+str(teamID)+'/roster') 
	jThisTeam=json.loads(rThisTeam.text) 
	#dump to file
	json.dump(jThisTeam, open('Team jsons\Team'+str(teamID)+'.json', 'w'))
	#Make unique list of player IDs for this team
	rosterIDList=[rosterslot['person']['id'] for rosterslot in jThisTeam['roster']]
	#add to the league-list of player IDs
	allRosterIDs.extend(rosterIDList)

#Test pulling player stats:
counter=[0]
for playerID in allRosterIDs[0:5]: #first 5 players (arbitrarily)
		
	#iterate through players in that roster and pull their stats
	#print('https://statsapi.web.nhl.com/api/v1/people/'+str(playerID)+'/stats')

	#pull from just one season
	myParams={
		'stats': 'statsSingleSeason',
		'season':20172018
	}

	#initialize empty player dictionary
	PlayerDict=[]
	#get stats on a player
	rThisGuy = requests.get('https://statsapi.web.nhl.com/api/v1/people/'+
		str(playerID), params=myParams)
	jThisGuy=json.loads(rThisGuy.text)
	rThisGuyStats = requests.get('https://statsapi.web.nhl.com/api/v1/people/'+	str(playerID)+'/stats', params=myParams)
	jThisGuyStats = json.loads(rThisGuyStats.text)
	#Make a dictionary entry for this guy
	print('...loading ' + jThisGuy['people'][0]['fullName'] +
		' (ID=' + str(playerID)+')')
	if jThisGuyStats['stats'][0]['splits']:
		#stats splits are populated (some times they're not for first-time callups)
		ThisPlayerProfile={**jThisGuy['people'][0], **jThisGuyStats['stats'][0]['splits'][0]['stat']}
		PlayerDict=ThisPlayerProfile.copy()
		print(len(PlayerDict))

json.dump(PlayerDict, open('activeplayers.json', 'w'))