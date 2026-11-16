from abc import ABC, abstractmethod
from board import ConnectBoard, Player

# Use this base class to create other agents
# e.g. class MinimaxAgent(BaseAgent):
#          .. other methods needed ..
#          def get_best_move(self, board, player):
#              """ Implementation here """ 
#          def get_last_search_tree(self):
#              """ Implementation here """ 

class BaseAgent(ABC):
    # Determines the best column to drop a disc.
    # Must also record the search tree data
    @abstractmethod
    def get_best_move(self, board: ConnectBoard, player: Player) -> int:
        pass

    # Returns the search tree dictionary from the most recent turn
    @abstractmethod
    def get_last_search_tree(self) -> dict:
        pass