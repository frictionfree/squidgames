import uuid
import random
import json
import datetime

class SumQuest:
    g_game_type  = 1 # currently supporting just the number breaking game
    min_number = 1
    max_number = 10000000

    def __init__(self):
        pass

    def get_unique_name(self) -> str:
        return "SumQuest v1.0"

    def new_game(self):
        min_threshold = random.randint(self.min_number, self.min_number + random.randint(1,300))
        max_threshold = random.randint(min_threshold, self.max_number - random.randint(1,300))
        parts = random.randint(100, 200)
        n = int((min_threshold + max_threshold)/2)*parts
        game_id = uuid.uuid4()

        game_parameters = {
            'id' : str(game_id),
            'NumberToBreak' : n,
            'Parts' : parts,
            'Min' : int((min_threshold+self.min_number)/2),
            'Max' : int((max_threshold+self.max_number)/2)
        }
    
        return game_parameters
    
    def check_solution(self, game_params : json, solution : json, duration : datetime.timedelta):
        """
        Validates a submitted solution for the SumQuest v1.0 game.
        Takes a JSON object with the parameters of the game, a JSON object containing the submitted solution 'as-in'
        and an object representing the time it took the player to produce the solution.
        Returns a tuple: True/False depending on whether the solution is valid , a score.
        """
        # Convert to an arrary of Integers...
        arr = solution['parts']
        parts = ([int(x) for x in arr[1:-1].split(',')])

        # Check the correctness of the solution
        is_valid =  ( sum(parts) == int(game_params["NumberToBreak"]) ) and \
                ( min(parts) >= int(game_params["Min"]) ) and \
                ( max(parts) <= int(game_params["Max"]) )
        
        EXPECTED_NETWORK_LATENCY_FOR_SUBMIT = 30000 # microseconds
        EXPECTED_COMPUTE_DURATION_PER_PART = 200 # microseconds
        bonus = EXPECTED_NETWORK_LATENCY_FOR_SUBMIT + EXPECTED_COMPUTE_DURATION_PER_PART* int(game_params["Parts"])  - duration.microseconds 

        bonus = bonus if bonus > 0 else 0
        score = 0
        if (is_valid) :
            # Scoring works as following... the player gets {parts} points
            score = 100 + bonus

        return is_valid, score