from agents.minimax import MinimaxAgent
from agents.alphabeta import AlphaBetaAgent
from agents.expectiminimax import ExpectedMinimaxAgent

# Allow changing of AI agent
# based on menu selection
class Selector:
    @staticmethod
    def create_agent(algorithm_name: str):
        if algorithm_name.lower() == "alpha-beta":
            return AlphaBetaAgent()
        elif algorithm_name.lower() == "expectiminimax":
            return ExpectedMinimaxAgent()
        else:
            return MinimaxAgent()