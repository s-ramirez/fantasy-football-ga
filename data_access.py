import psycopg2
import psycopg2.extras

class DataAccess(object):
    def __init__(self):
        connect_str = "dbname='epl' user='postgres' host='localhost' " + \
                  "password='pass'"
        self.conn = psycopg2.connect(connect_str)

    def get_gameweeks(self, start, end):
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""SELECT epl_player_histories.epl_player_system_id, epl_player_histories.points, epl_player_histories.value, epl_players.name, epl_players.epl_team_name, epl_players.position, epl_player_histories.gameweek \
                FROM public.epl_player_histories, public.epl_players  \
                WHERE epl_players.system_id = epl_player_histories.epl_player_system_id \
                AND epl_player_histories.gameweek >= {} AND epl_player_histories.gameweek <= {}""".format(start, end))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Invalid db name, user or password")
            print(e)
            return False
    def get_players(self,gameweek):
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""SELECT epl_player_histories.epl_player_system_id, epl_player_histories.points, epl_player_histories.value, epl_players.name, epl_players.epl_team_name, epl_players.position, epl_player_histories.gameweek \
                FROM public.epl_player_histories, public.epl_players  \
                WHERE epl_players.system_id = epl_player_histories.epl_player_system_id \
                AND epl_player_histories.gameweek = {}""".format(gameweek))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Invalid db name, user or password")
            print(e)
            return False
