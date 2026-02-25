from axelrod.action import Action
from axelrod.strategies import Defector as axlDefector
from axelrod.strategies import Cooperator as axlCooperator
from axelrod.strategies import Alternator as axlAlternator
from axelrodVoice import Player

class Liar(axlDefector, Player):
    name = "LIAR"
    def strategy_voice(self, opponent: Player) -> Action:
        return Action.C

class Defector(axlDefector, Player):
    name = "DEFT"
    def strategy_voice(self, opponent: Player) -> Action:
        return Action.D

class Cooperator(axlCooperator, Player):
    name = "COOP"
    def strategy_voice(self, opponent: Player) -> Action:
        return Action.C

class AllBarkNoBite(axlCooperator, Player):
    name = "ABNB"
    def strategy_voice(self, opponent: Player) -> Action:
        return Action.D


class Alternator(axlAlternator, Player):
    name = "ALTRxx"

    def strategy_voice(self, opponent: Player) -> Action:
        if len(self.history_voice) == 0: return Action.C
        else: return Action.flip( self.history_voice[-1] )


class AlternatorCX(axlAlternator, Player):
    name = "ALTRcx"

    def strategy_voice(self, opponent: Player) -> Action:
        return Action.C