from data_layer import *
from server import *
import argparse

g_sql_server_host = "tcp:db551849.database.windows.net,1433"
g_sql_database_name = "gameusersdb"
g_sql_user_name = "gameadmin"
g_sql_user_password = ""
   
def main():
    parser = argparse.ArgumentParser(
                    prog='GameServer',
                    description='Allow game clients to connect, pick up tasks and send back solutions.',
                    epilog='Enjoy')
    
    parser.add_argument('-p', '--adminDBPassword')
    args = parser.parse_args()
    
    data_layer = DataLayer(g_sql_server_host, g_sql_user_name, args.adminDBPassword, g_sql_database_name)

    sum_quest = SumQuest()
    game_server.initialize_game_server(data_layer, {sum_quest.get_unique_name() : sum_quest})
    game_server.init_http_server()

if __name__ == "__main__":
    main()