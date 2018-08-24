# NHLStatsScraper
Pulls stats down from the NHL API and makes 'em crunchable for fantasy hockey picks.

## To Do
Things to add, in broad terms:
1. Pull 2017-2018 stats for all players
2. Organize into fantasy stats array
    * Pull list of stats for the league!
3. Make super secret functions to make derived stats for picking
4. Make Drafting application. Ideas:
    * Load player JSONs from file - this'll let manual edits take effect (and be faster)
    * Remove players as they're drafted - fuzzy matching player names?
    * Sort by position (including matching folks with multiple positions, eg C/LW)
    * Sort by chosen metric
    * Filter by team - don't get too loaded on one team, mostly for scheduling reasons
        * Will need to update with off-season trades - must be a tracker available somewhere we can use
    * Filter by conference? Don't think this is useful.
    * I want to type into console and have things work.
        * draft connor mcdavid -> 'Drafted Connor McDavid' -> remove him from the list.
        * list C -> 'List forwards'
        * list C G A PIM -> 'List forwards by Goals, then Assists, then PIM
        * hide team PIT -> 'Remove team PIT'
        * show team PIT
