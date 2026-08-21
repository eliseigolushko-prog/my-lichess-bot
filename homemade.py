"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
from stockfish import Stockfish
import requests


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ChessManager(MinimalEngine):
    """An example engine that all homemade engines inherit."""


# Bot names and ideas from tom7's excellent eloWorld video

class ComboEngine(ChessManager):
    """
    Get a move using multiple different methods.

    This engine demonstrates how one can use `time_limit`, `draw_offered`, and `root_moves`.
    """

    def get_api(username):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(
                url=f"https://lichess.org/api/user/{username}/current-game",
                params={
                    "moves": "false",
                    "pgnInJson": "false",
                    "tags": "true",
                    "clocks": "false",
                    "evals": "true",
                    "accuracy": "false",
                    "opening": "false",
                    "division": "false",
                    "literate": "false"
                },
                headers=headers
                )
            
        except Exception as e:

            logger.info(f"Error {e}")

    def search(self,
               board: chess.Board,
               time_limit: Limit,
               ponder: bool,  # noqa: ARG002
               draw_offered: bool,
               root_moves: MOVE) -> PlayResult:
        """
        Choose a move using multiple different methods.

        :param board: The current position.
        :param time_limit: Conditions for how long the engine can search (e.g. we have 10 seconds and search up to depth 10).
        :param ponder: Whether the engine can ponder after playing a move.
        :param draw_offered: Whether the bot was offered a draw.
        :param root_moves: If it is a list, the engine should only play a move that is in `root_moves`.
        :return: The move to play.
        """
        if isinstance(time_limit.time, int):
            my_time = time_limit.time
            my_inc = 0
        elif board.turn == chess.WHITE:
            my_time = time_limit.white_clock if isinstance(time_limit.white_clock, int) else 0
            my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, int) else 0
        else:
            my_time = time_limit.black_clock if isinstance(time_limit.black_clock, int) else 0
            my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, int) else 0

        possible_moves = root_moves if isinstance(root_moves, list) else list(board.legal_moves)

        if my_time / 60 + my_inc < 10:
            stockfish = Stockfish(path="/Users/portmare/Downloads/stockfish/stockfish-macos-m1-apple-silicon", depth=8, parameters={"Minimum Thinking Time": 1, "UCI_Elo": 2000})
            fen_str = board.fen()
            stockfish.set_fen_position(fen_str)
            move = stockfish.get_best_move_time(1000)
            legal = chess.Move.from_uci(move)

        elif my_time / 60 + my_inc < 20 and not my_time / 60 + my_inc < 10:
            # Choose the first move alphabetically in uci representation.
            stockfish = Stockfish(path="/Users/portmare/Downloads/stockfish/stockfish-macos-m1-apple-silicon", depth=10, parameters={"Minimum Thinking Time": 1, "UCI_Elo": 2000})
            fen_str = board.fen()
            stockfish.set_fen_position(fen_str)
            move = stockfish.get_best_move_time(1500)
            legal = chess.Move.from_uci(move)

        else:
            stockfish = Stockfish(path="/Users/portmare/Downloads/stockfish/stockfish-macos-m1-apple-silicon", depth=12, parameters={"Minimum Thinking Time": 1, "UCI_Elo": 2000})
            fen_str = board.fen()
            stockfish.set_fen_position(fen_str)
            move = stockfish.get_best_move_time(2000)
            legal = chess.Move.from_uci(move)

        return PlayResult(legal, None, draw_offered=draw_offered)