from fuzzywuzzy import process
from operator import itemgetter
import csv
import sys
import json

config=json.load(open('config.json', 'r'))
players=list(csv.DictReader(open(sys.argv[1], 'r')))
#Store all fantasy team names (eg teams to draft to)
allFantasyTeams=config['allFantasyTeams']
allFantasyTeams.append('all')

#Store all possible positions:
allPositions=['RW', 'LW', 'C', 'D', 'G', 'S'] #S for skater

defaultStats=config['defaultStats']
#some manual cleanup of stats
intcolumns=config['intcolumns']
floatcolumns=config['floatcolumns']
for player in players:
	for col in intcolumns:
		player[col]=int(player[col])
	for col in floatcolumns:
		player[col]=float(player[col])
allPlayerNames = [player['FullName'] for player in players]

#Pull stat names
allColumnNames=[str(key) for key in players[0].keys()]

#Store team names
#restrict to most recent team 
for player in players: 
	player['Team']=player['Team'][-3:] 
allTeamNames = list(set([player['Team'] for player in players]))
shownTeamNames = allTeamNames[:] #copy values, not by reference

#These are all the valid commands for this program
allCommands=['rem', 'add', 'ls', 'hide', 'show', 'tls', 'saveas']

playersToDisplay=30

while True:
	userInput=input('$$$>')
	if userInput == 'exit':
		#quit
		break
	if userInput.isspace() or userInput=='':
		#Only whitespace - just ask again for input
		pass
	else:
		userInput = userInput.split() #break up by spaces
		command=userInput[0]
		commandMatch = process.extractOne(command, allCommands)
		commandMatch = commandMatch[0]
		
		if len(userInput)==1:
			print('Need more arguments.')		
		elif commandMatch == 'rem' or commandMatch == 'add':
			if commandMatch=='rem':
				#Last argument is the team to draft to
				player=''
				for inputString in userInput[1:-1]:
					player+=inputString + ' '
				fantasyTeam=userInput[-1]
				print('player: ' + player + '\nfantasyTeam: ' + fantasyTeam)
				fantasyTeamMatch=process.extractOne(fantasyTeam, allFantasyTeams)
				fantasyTeamMatch=fantasyTeamMatch[0]
			elif commandMatch=='add':
				player=''
				for inputString in userInput[1:]:
					player+=inputString + ''

			#match inputted player name
			playerMatch = process.extractOne(player, allPlayerNames)
			playerMatch = playerMatch[0]
			
			#loop through all players and set the flag
			for player in players: 
				if player['FullName']==playerMatch:
					#We've matched the player
					if commandMatch == 'rem':					
						player['FantasyTeam'] = fantasyTeamMatch
						print('Setting ' + playerMatch + ' as drafted to team ' + fantasyTeamMatch + ', and hiding in list.')
					elif commandMatch == 'add':
						player['FantasyTeam'] = 'None'
						print('Setting ' + playerMatch + ' as available to draft, and showing in list.')

		elif commandMatch =='hide' or commandMatch == 'show':			
			#Hide or show a team from display
			team=userInput[1]
			teamMatch=process.extractOne(team, allTeamNames)
			teamMatch=teamMatch[0]

			if commandMatch == 'hide':
				if teamMatch in shownTeamNames:
					shownTeamNames.remove(teamMatch)
				print('Hiding players from team ' + teamMatch + ' in the draft list')
			elif commandMatch == 'show':
				if teamMatch not in shownTeamNames:
					shownTeamNames.append(teamMatch)
				print('Showing players from team ' + teamMatch + ' in the draft list.')
			
		elif commandMatch == 'ls':
			#List players for drafting. Next arguments are column names. JUST ONE FOR NOW
			sortcols=list()
			pos=userInput[1]
			posMatch=process.extractOne(pos, allPositions)
			posMatch=posMatch[0]
				
			if posMatch=='S':
				posMatch=['RW', 'C', 'LW', 'D']
			else:
				#Put in a list for the multiple matching
				posMatch=[ posMatch]
			
			for argument in userInput[2:]:
				#case insensitive compare, assuming lazy user
				thisCol=process.extractOne(argument, [col for col in allColumnNames])
				sortcols.append(thisCol[0])
			
			if len(sortcols)==0:
				sortcols=defaultStats
			
			#Sort list as per user request. * unpacks the list (equivalent to listing out the entries individually)
			thisDisplay = sorted(players, key=itemgetter(*sortcols), reverse=True) 
			#Print titles. Pad strings to fixed lengths (ljust, rjust)
			displayString='FullName'.ljust(20) +' Position' + ' Team'
			for col in sortcols:
				displayString += ' ' + col.rjust(4) 
			print(displayString)
			#Print players. Pad strings to fixed lengths (ljust, rjust)
			displayed=0
			for player in thisDisplay:
				if player['FantasyTeam'] == 'None' and player['Team'] in shownTeamNames and any(x in player['Position'] for x in posMatch):
					#print player
					displayString=player['FullName'].ljust(20)[-25:] + player['Position'].rjust(9)+player['Team'].rjust(5)
					for col in sortcols:
						displayString += ' ' + str(player[col]).rjust(4)[0:4] 
					print(displayString)
					displayed+=1
				if displayed >= playersToDisplay:
					print('<....................... More players hidden>')
					break
		elif commandMatch == 'saveas':
			filename = userInput[1]
			if filename[-4:] is not '.csv':
				filename=filename+'.csv'
			
			#pull fieldnames from the players list
			outputFieldNames=list(players[0].keys())
			with open(filename, 'w') as f:
				for field in outputFieldNames:
					f.write(field+',')
				f.write('\n')
				for player in players:
					for field in outputFieldNames:
						f.write(str(player[field])+',')
					f.write('\n')
			print('Output written to ' + filename)
		elif commandMatch == 'tls':
			#List fantasy teams
			fantasyTeam=userInput[1]
			fantasyTeamMatch=process.extractOne(fantasyTeam, allFantasyTeams)
			fantasyTeamMatch=fantasyTeamMatch[0]
			if fantasyTeamMatch=='all':
				#display for every team
				fantasyTeamMatch=allFantasyTeams[:-2]
			else:
				#embed in list for consistency
				fantasyTeamMatch=[fantasyTeamMatch]
			
			#Match stats
			sortcols=[]
			for argument in userInput[2:]:
				thisCol=process.extractOne(argument, [col for col in allColumnNames])
				sortcols.append(thisCol[0])
			if len(sortcols)==0:
				sortcols=defaultStats

			#Print titles. Pad strings to fixed lengths (ljust, rjust)
			print('########## Displaying totals by fantasy teams ##########')
			displayString='FANTASY TEAM'.ljust(15)
			for col in sortcols:
				displayString += ' ' + col.rjust(4) 
			print(displayString)

			for team in fantasyTeamMatch:					
				#PRINT TOTALS
				fantasyTeamTotals=dict()
				for col in sortcols:
					fantasyTeamTotals[col]=0
				for player in players:
					if player['FantasyTeam'] == team:
						for col in sortcols:
							fantasyTeamTotals[col] += player[col] 
				displayString=team.ljust(15)
				for col in sortcols:
					displayString += ' ' + str(fantasyTeamTotals[col]).rjust(4)[0:4] 
				print(displayString)		