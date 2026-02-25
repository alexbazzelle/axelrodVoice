import axelrod.match
import axelrod.classifier
from axelrod import Action
C, D = Action.C, Action.D

"""
Updates to Match class:
- added result_voice:List
- updated simultaneous_play to store results
- added debug:int printing for play and simultaneous_play

Set debug=1 to print matches as
    ["X" "Y"] [.X. .Y.]
    ["X" "Y"] [.X. .Y.]
    ...
    
Set debug=2 to print matches as
    xyXY xyXY ...
"""

class Match(axelrod.match.Match):
    def __init__(
        self,
        players,
        turns=None,
        prob_end=None,
        game=None,
        deterministic_cache=None,
        noise=0,
        match_attributes=None,
        reset=True,
        seed=None,
    ):
        super().__init__(players, turns, prob_end,
            game, deterministic_cache, noise,
            match_attributes, reset, seed)
        self.debug = 0
        self.result_voice = []


    def play(self):
        if self.prob_end:
            r = self._random.random()
            turns = min(super().sample_length(self.prob_end, r), self.turns)
        else:
            turns = self.turns
        cache_key = (self.players[0], self.players[1])

        if self._stochastic or not self._cached_enough_turns(cache_key, turns):
            for p in self.players:
                if self.reset:
                    p.reset()
                p.set_match_attributes(**self.match_attributes)
                # Generate a random seed for the player, if stochastic
                if axelrod.classifier.Classifiers["stochastic"](p):
                    p.set_seed(self._random.random_seed_int())
            result = []
            for _ in range(turns):
                plays = self.simultaneous_play(
                    self.players[0], self.players[1], self.noise
                )
                result.append(plays)

            # NEW: debug printing ["X" "Y"] [.X. .Y.]
            if self.debug == 1:
                print( f"P1 = {self.players[0].name}")
                print( f"P2 = {self.players[1].name}")
                print( "[P1v P2v] [P1c P2c] (0)")
                p1v, p1c, p2v, p2c = [], [], [], []
                for i in range (0, len(self.players[0].history)):
                    if self.players[0].history_voice[i] == axelrod.action.Action.C: p1v.append("\033[32mc\033[39m\033[49m")
                    else: p1v.append("\033[31md\033[39m\033[49m")
                    if self.players[1].history_voice[i] == axelrod.action.Action.C: p2v.append("\033[32mc\033[39m\033[49m")
                    else: p2v.append("\033[31md\033[39m\033[49m")
                    if self.players[0].history[i] == axelrod.action.Action.C: p1c.append("\033[92mC\033[39m\033[49m")
                    else: p1c.append("\033[91mD\033[39m\033[49m")
                    if self.players[1].history[i] == axelrod.action.Action.C: p2c.append("\033[92mC\033[39m\033[49m")
                    else: p2c.append("\033[91mD\033[39m\033[49m")

                for i in range (0, len(self.players[0].history)):
                    print(f"{p1v[i]}{p2v[i]}{p1c[i]}{p2c[i]} ({i+1})")
            # END NEW

            if self._cache_update_required:
                self._cache[cache_key] = result
        else:
            result = self._cache[cache_key][:turns]

        self.result = result
        return result
    

    def simultaneous_play(self, player, coplayer, noise=0):
        # NEW: record voice responses
        v1, v2 = player.strategy_voice(coplayer), coplayer.strategy_voice(player)
        player.update_history_voice(v1, v2)
        coplayer.update_history_voice(v2, v1)
        self.result_voice.append((v1, v2))
        # END NEW

        """This pits two players against each other."""
        s1, s2 = player.strategy(coplayer), coplayer.strategy(player)
        if noise:
            # Note this uses the Match classes random generator, not either
            # player's random generator. A player shouldn't be able to
            # predict the outcome of this noise flip.
            s1 = self._random.random_flip(s1, noise)
            s2 = self._random.random_flip(s2, noise)
        player.update_history(s1, s2)
        coplayer.update_history(s2, s1)
        # NEW: update complete history
        player.update_history_tuples()
        coplayer.update_history_tuples()
        # NEW END

        # NEW: debug printing xyXY
        if self.debug == 2:
            out = ""
            for voiceResponse in [v1, v2]:
                if voiceResponse == axelrod.action.Action.C: out += "\033[32mc"
                else: out += "\033[31md"
            for choiceResponse in [s1, s2]:
                if choiceResponse == axelrod.action.Action.C: out += "\033[92mC"
                else: out += "\033[91mD"
            print(f"{out} \033[39m\033[49m", end="")
        # END NEW
        return s1, s2