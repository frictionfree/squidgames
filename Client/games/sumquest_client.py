import random
import json

class SumQuest_v1_0_Client : 
    @staticmethod
    def solve_puzzle(number_to_break, parts, min_threshold, max_threshold) :
        solution = []
        if (number_to_break > (parts * max_threshold) or number_to_break < (parts * min_threshold)) :
            return solution
        
        for n in range(parts) :
            new_min = max(min_threshold, number_to_break - (parts - n - 1)*max_threshold)
            new_max = min(max_threshold, number_to_break - (parts - n - 1)*min_threshold)

            next_number = random.randint(new_min, new_max)
            solution.append(next_number)
            number_to_break = number_to_break - next_number

        return solution
    
    @staticmethod
    def play_game(game_params : json) :
        """
        Takes a JSON blob of game parameters as it was fetched from the SumQuest v1.0 provider on the Squid Game Server
        and returns a JSON blob adhering to the specifics of the SumQuest v1.0 game server expectations.
        """
        solution = SumQuest_v1_0_Client.solve_puzzle(int(game_params.get("NumberToBreak")), int(game_params.get("Parts")), int(game_params.get("Min")), int(game_params.get("Max")))
        print (f'Solution: {0}', solution)

        solution_pack = {
                "id" : game_params.get("id"),
                "parts" : str(solution)
        }

        return solution_pack

    @staticmethod
    def name() -> (str) :
        """ Returns a unique name for the SumQuest game """
        return "SumQuest v1.0"