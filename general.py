# users = [390,7412,41553,49,88893,740062,2069537,683,28835,4930,870983,116553,41447,4697,198740,19992,2088,36589,140261,165692,21798,64069,38039,1293102,385903,1147293,2413,406419,2230710,108076,535131,1483923,834570,167896,2199038,190607,798,37578,224674,3123,475,6907,44880,11676,51778,107594,2222,881740,71976,113854,1953664,274036,413452,38038,243427,82035,961594,5442,125470,691000,98612,120,453,30335,1001362,269023,157284,76051,303819,55583,1603958,261,38757,552636,97872,832729,179910,479233,8699,59943,890,11865,77083,802730,853722,534536,1366410,524,1786,58398,2072064,80,18785,486095,718,2554291,1994,422214,25749,24925]
import psycopg2
import psycopg2.extras

users = [390,7412,41553]

connect_str = "dbname='epl' user='postgres' host='localhost' " + \
          "password='Cartagines13'"
conn = psycopg2.connect(connect_str)

for i in users:
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT epl_player_histories.points, fantasy_team_gameweek_results.fantasy_team_system_id,  fantasy_teams.name,  fantasy_team_gameweek_results.gameweek \
            FROM public.fantasy_team_gameweek_results,  public.epl_player_histories,  public.fantasy_teams \
            WHERE fantasy_team_gameweek_results.epl_player_system_id = epl_player_histories.epl_player_system_id AND fantasy_team_gameweek_results.gameweek = epl_player_histories.gameweek AND \
            fantasy_teams.system_id = fantasy_team_gameweek_results.fantasy_team_system_id AND fantasy_teams.system_id = {};""".format(i))
        rows = cursor.fetchall()
        total = 0
        for row in rows:
            total += row['points']
        print('Player {} got {} points'.format(i, total))

    except Exception as e:
        print("Invalid db name, user or password")
        print(e)
