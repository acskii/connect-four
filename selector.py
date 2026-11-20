from agents.minimax import MinimaxAgent
from agents.alphabeta import AlphaBetaAgent
from agents.expectiminimax import ExpectedMinimaxAgent

# Allow changing of AI agent
# based on menu selection
class Selector:
    ALGORITHMS = ["Minimax", "Alpha-Beta", "Expectiminimax"]

    @staticmethod
    def create_agent(algorithm_name: str, depth: int = 4):
        if algorithm_name.lower() == "alpha-beta":
            return AlphaBetaAgent(depth)
        elif algorithm_name.lower() == "expectiminimax":
            return ExpectedMinimaxAgent(depth)
        else:
            return MinimaxAgent(depth)