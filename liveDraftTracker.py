from fuzzywuzzy import process
from operator import itemgetter
import csv
import sys

players=list(csv.DictReader(open(sys.argv[1], 'r')))
#some manual cleanup of stats
intcolumns = ['GP', 'G', 'A', 'PIM',  'SOG', 'HIT', 'BLK', 'PPP', 'SHP', 'W', 'SO']
floatcolumns = ['TOI', 'SVP', 'GAA']
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

#Pythonify field for player draft tracking
for player in players:
	if player['Available'] == 'TRUE':
		player['Available']=True
	else:
		player['Available']=False

#Store all possible positions:
allPositions=['RW', 'LW', 'C', 'D', 'G', 'S'] #S for skater
#These are all the valid commands for this program
allCommands=['rem', 'add', 'ls', 'hide', 'show', 'saveas', 'def']

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
		
		if commandMatch == 'rem' or commandMatch == 'add':
			#remove or add a player as eligible to draft
			#match the player name
			if len(userInput)==1:
				#didn't specify a player - lets just use Pageau
				player='Jean-Gabriel Pageau'
			elif len(userInput)==2:
				#only one name
				player=userInput[1]
			else:
				#use next two arguments as first/last - ignore any extras.
				player=userInput[1] + ' ' + userInput [2]
			#match input
			playerMatch = process.extractOne(player, allPlayerNames)
			playerMatch = playerMatch[0]
			
			#loop through all players and set the flag
			for player in players: 
				if player['FullName']==playerMatch:
					#We've matched the player
					if commandMatch == 'rem':					
						player['Available'] = False
						print('Setting ' + playerMatch + ' as unavailable to draft, and hiding in list.')
					elif commandMatch == 'add':
						player['Available'] = True
						print('Setting ' + playerMatch + ' as available to draft, and showing in list.')

		elif commandMatch =='hide' or commandMatch == 'show':			
			#Hide or show a team from display
			if len(userInput)==1:
				print('Need 1+ argument for this command.')
			else:
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
			if len(userInput)==1:
				#Default to skaters
				posMatch='S'
			else:
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
				#default to goals
				sortcols=['G']
			
			#Sort list as per user request. * unpacks the list (equivalent to listing out the entries individually)
			thisDisplay = sorted(players, key=itemgetter(*sortcols), reverse=True) 
			#Print titles. Pad strings to fixed lengths (ljust, rjust)
			displayString='FullName'.ljust(20) +' Position' + ' Team'
			for col in sortcols:
				displayString += ' ' + col.rjust(5) 
			print(displayString)
			#Print players. Pad strings to fixed lengths (ljust, rjust)
			displayed=0
			for player in thisDisplay:
				if player['Available'] == True and player['Team'] in shownTeamNames and any(x in player['Position'] for x in posMatch):
					#print player
					displayString=player['FullName'].ljust(20)[-25:] + player['Position'].rjust(9)+player['Team'].rjust(5)
					for col in sortcols:
						displayString += ' ' + str(player[col]).rjust(5) 
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
		#elif commandMatch == 'def':
		#	#Define new statistic. Parse out name and settings: 
		#	stat=userInput[1]
		#	if userInput[2]=='gp' or userInput[3]='gp':
		#		GPScale=True
		#	else:
		#		GPScale=False
		#	if userInput[2]=='z' or userInput[3]='z':
		#		ZScale=True
		#	else:
		#		ZScale=False
		#	#Evaluate the rest as a python function:
		#	#FIGURE ME OUT