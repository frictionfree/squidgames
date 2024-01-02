import pyodbc 
from pyodbc import OperationalError
import pandas as pd
import json
from datetime import datetime
import base64

class DataLayer :
    connection = None

    def __init__(self, host_name, user_name, user_password, db_name) -> None:
        self.create_db_connection(host_name, user_name, user_password, db_name)

    def create_db_connection(self, host_name, user_name, user_password, db_name) ->None:
        connection_string = "Driver={ODBC Driver 17 for SQL Server};"+"Server={0};".format(host_name) + "Database={0};".format(db_name) + "UID={0};".format(user_name) + "PWD={0};".format(user_password) + "Trusted_Connection=no;"
        MAX_CONNECTION_ATTEMPTS = 4

        retry_count = 0
        need_to_try = True

        while (need_to_try) :
            try :
                need_to_try = False
                self.connection = pyodbc.connect(connection_string)
                # Success
                print("Game server MS SQL Database connection successful on " , host_name)
            except OperationalError :
                retry_count = retry_count + 1
                if (retry_count < MAX_CONNECTION_ATTEMPTS) :
                    need_to_try = True
                    print ("Attempt to connect to {0} failed, will retry".format(host_name))
                else :
                    print ("Attempt to connect to {0} failed all retries".format(host_name))
                    raise Exception("Cannot proceed without DataBase connectivity")
            
    def read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        finally:    
            return result

    def execute_query(self, query):
        cursor = self.connection.cursor()
        result = None

        cursor.execute(query)
        result = self.connection.commit()

        return result

    def restore_game(self, game_id) -> tuple:
        """
        Takes an identifier of an active game, returns a tuple of (parameters, player id, duration
        between when the game was generated to now, game_type).
        Returned 'parameters' is a JSON object that is understood by the specific game provider
        associated with game_type, player_id and game_type.
        """
        FIND_GAME_BY_ID_QUERY = "SELECT * FROM Games WHERE Id = '{0}' AND GameStatus = 0;"
              
        results = self.read_query(FIND_GAME_BY_ID_QUERY.format(game_id))
        if results == None or len(results) == 0 :
            raise Exception("Invalid game id {0}".format(game_id))
        
        (game_id, gameStatus, game_type, game_params, game_time, player_id, completed_time, score) = results[0]
        
        # For fareness, try to stop the game's stop watch as soon as possible
        duration = datetime.utcnow() - game_time

        # The paramters are stored in DB in base64 encoding (to allow the game to store any schema).
        # After decoding it looks like this: b"{'attribute1_name': 'string_value1..', 'attribute2_name': int_value, ... }"
        # So loading into a json object requires
        # 1. trimming the heading b" and trailing "
        # 2. replacing ' with " accross the entire block
        game_params_decoded = json.loads(str(base64.b64decode(game_params))[2:-1].replace("'", '"'))

        return (game_params_decoded, player_id, duration, game_type)
    
    def store_new_game(self, game_type : str, game_id : str, game_params : json, user_id : str) :
        STORE_GAME_QUERY = "INSERT INTO Games (Id, GameStatus, GameType, Params, Created, UserID) VALUES ('{0}', {1}, '{2}', {3}, '{4}', '{5}');"
    
        message_bytes = str(game_params).encode('ascii')
        game_params_encoded = str(base64.b64encode(message_bytes))[1:]

        query_to_run = STORE_GAME_QUERY.format(game_id, 0, game_type, game_params_encoded, datetime.utcnow().strftime('%F %T.%f')[:], user_id )

        # print (storeGameQueryEncoded2)
        results = self.execute_query(query_to_run)
