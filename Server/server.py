from flask import Flask, jsonify
from flask import request, send_from_directory
from data_layer import *
from games.sumquest import SumQuest
import base64

flask_app = Flask(__name__)

class GameServer() :
    QUOTA_PER_PLAYER = 50

    def __init__(self) -> None:
        pass

    def initialize_game_server(self, data_layer : DataLayer, list_of_games : dict) -> None:
        """
        Takes an initialized DataLayer object and a dictionary of registered games. Returns nothing.
        After this call completes, the init_http_server() can be called to start accepting http calls.
        Additional game objects can be registered after this call with register_game()
        """
        self.data_layer = data_layer
        self.registered_games = list_of_games 
        self.logged_on_users = dict()

    def register_game(self, new_game):
        """
        Takes a duck-type game object. Returns nothing.
        Can be called at any time.
        """
        self.registered_games[new_game.get_unique_name()] = new_game

    def submit(self):
        """
        Handles a POST request from the player where the body is a JSON containing the 'id' and the specific 
        solution of a quiz. The function relays the validation of the solution to the relevant game provider
        for the specific solution. Given the solution is correct then the function also sets the game's DB
        record to indicate the quiz was complete and captures the duration between the generation of the game
        to the submission of the solution.
        """

        # Authorize the request based on the authorization header
        auth_header = request.headers.get('authorization')
        if self.logged_on_users != None :
            if not (auth_header in self.logged_on_users) :
                return jsonify({"error": "Invalid authorization header, please re-authenticate."}), 403
        
        body = request.get_json()

        if (not ('id' in body)) :
            return jsonify({"error": "solution JSON payload must include a root level attribute 'id'."}), 400
        
        game_id = str(body['id'])

        # Load the saved game record from the DB by the game id
        (game_params, player_id, duration, game_index) = self.data_layer.restore_game(game_id)

        # Invoke the desired game provider to generate the new game
        is_valid_solution, score = self.registered_games[game_index].check_solution(game_params, body, duration)

        if (is_valid_solution) :
            response = jsonify({"valid": "true", "duration" : str(duration), "score" : score})
        else :
            response = jsonify({"valid": "false", "duration" : str(duration), "score" : score}) 
        
        # Finally mark the game as complete
        END_GAME_QUERY = "update Games set GameStatus = 1, Completed = '{0}', Score = {1} where Id = '{2}';"
        self.data_layer.execute_query(END_GAME_QUERY.format(datetime.utcnow().strftime('%F %T.%f')[:], score, str(game_id)))

        return response

    def validate_token(self, token : tuple) -> str:
        """
        Takes a tuple(string username, int roles) representing an authentication token issued by the authenticate() method.
        Returns the user name to which the token was issued or None if invalid token.
        """
        if self.logged_on_users != None :
            if token in self.logged_on_users :
                return self.logged_on_users[token][0]
        else :
            return None

    def get_game(self):
        """
        Handles a HTTP Get request to start a new game. Takes no parameters.
        The HTTP request is expected to include an authorization header and a URL parameter 'game_name' to specify the game.
        Upon success returns 200 OK with a JSON body with the paramters of a new game (exact schema depends on the game)
        """
        username = None
        auth_header = request.headers.get('authorization')
        game_index = request.args.get('game_name')

        username = self.validate_token(auth_header)
        if username == None :
                return jsonify({"error": "Invalid authorization header"}), 403
        
        if self.is_quota_exceeded(username) :
            response = jsonify({"error": "Quota exceeded for player {0}".format(username)})
            return response, 403     
        
        if ( not (game_index in self.registered_games.keys()) ) :
            response = jsonify({"error": "Requested game index out of range: {0}".format(game_index)})
            return response, 400
        
        # Invoke the desired game provider to generate the new game
        game_parameters = self.registered_games[game_index].new_game()
        response = jsonify({'game_params' : game_parameters})

        self.data_layer.store_new_game(game_index, str(game_parameters["id"]), game_parameters, username)

        return response

    def is_quota_exceeded(self, player_id : str) -> bool:
        """
        Takes a player_id string and checks the number of games (in all states) associated with the player.
        Returns True if the quota has been reached or False otherwise.
        """
        COUNT_GAMES_QUERY = "SELECT COUNT(*) FROM Games WHERE UserID = '{0}';"
        # Validate that user did not exceed the games quota
        results = self.data_layer.read_query(COUNT_GAMES_QUERY.format(player_id))
        if results == None or len(results) == 0 :
            return False
        elif (int(results[0][0]) < self.QUOTA_PER_PLAYER) :
            return False
        else :
            return True

    def authenticate(self):
        """
        Handles a HTTP Get request to obtain an authentication token. Takes no parameters.
        The HTTP request is expected to include two URL parameters: 'username' and 'password'.
        Upon success returns 200 OK with a JSON body with two attributes: 'id' echoeing the name of the player
        and 'token' containing a volatile token.
        """
        username = request.args.get('username')
        password = request.args.get('password')

        AUTHENTICATION_QUERY = "select UserID, Roles from Users WHERE UserID = '{0}' AND Passcode = '{1}'"
        q1 = AUTHENTICATION_QUERY.format(username, password)
        results = self.data_layer.read_query(q1)

        if results == None or len(results) == 0 :
            auth_response = jsonify({'error': "Invalid user name or password"})
            return auth_response, 403
        else :
            # results[0] => first record. results[0][0] => userid fetched from the DB
            roles = int(results[0][1])
            token = str(abs(hash(str(results[0][0]))))
            auth_token = {
                'id' : username,
                'token' : token
            }
            auth_response = jsonify({'authentication': auth_token})
            
            self.logged_on_users[token] = (username, roles)
        return auth_response

    def init_http_server(self) :
        flask_app.run(debug=True)

game_server = GameServer()

# Static assignments of accessor
@flask_app.route('/gameserver/api/v1.0/authenticate', methods=['GET'])
def authenticate():
    return game_server.authenticate()

@flask_app.route('/gameserver/api/v1.0/getgame', methods=['GET'])
def get_game():
    return game_server.get_game()

@flask_app.route('/gameserver/api/v1.0/submit', methods=['POST'])
def submit():
    return game_server.submit()

# Static html pages
@flask_app.route('/html/<path:path>')
def server_static_content(path):
    if (path != "login.html") :
        authenticated = False
        if ("SquidAuthCookie" in request.cookies.keys()) :
            authCookie = request.cookies["SquidAuthCookie"]
            if (None != game_server.validate_token(authCookie)):
                authenticated = True

        # No valid auth cookie was found
        if (not authenticated) :
            return send_from_directory('html', "login.html")
        
    return send_from_directory('html', path)