from otree.api import *
import numpy as np
from otree.models import player
import random


class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = 2

    inc_1 = np.array([33, 36])
    inc_2 = np.array([[70, 20], [66, 24], [60, 18]])
    pairs = np.zeros((len(inc_1)*len(inc_2), 3))
    k=0
    for i in inc_1:
        for j in inc_2:
            pairs[k,0] = i
            pairs[k,1:3] = j
            k=k+1
    np.random.shuffle(pairs)
    NUM_ROUNDS = (len(inc_1)*len(inc_2))

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    today = models.IntegerField()
    tomorrow_high = models.IntegerField()
    tomorrow_low = models.IntegerField()
    savings = models.IntegerField()
    period_chosen = models.IntegerField()
    risky_chosen = models.IntegerField()

def set_payoffs(player: Player):
    player.period_chosen = random.randint(1, 2)
    player.risky_chosen = random.randint(1, 2)
    if player.period_chosen == 1:
        payoff = player.today - player.savings
    else:
        if player.risky_chosen == 1:
            payoff = player.tomorrow_high + player.savings
        else:
            payoff = player.tomorrow_low + player.savings
    return payoff

# PAGES
class InvestmentDecision(Page):
    form_model = 'player'
    form_fields = ['today', 'tomorrow_high', 'tomorrow_low', 'savings']
    @staticmethod
    def vars_for_template(player: Player):
        r = player.round_number
        return{
            "today": C.pairs[r-1,0],
            "tomorrow_high": C.pairs[r-1,1],
            "tomorrow_low": C.pairs[r-1, 2],
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.payoff = set_payoffs(player)

class ResultsWaitPage(WaitPage):
    pass

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player: Player):
        decision_chosen = random.randint(1, C.NUM_ROUNDS)
        player.participant.payoff = player.in_round(decision_chosen).payoff
        return{
            "payoff": player.participant.payoff_plus_participation_fee(),
            "today": player.in_round(decision_chosen).today,
            "tomorrow_high": player.in_round(decision_chosen).tomorrow_high,
            "tomorrow_low": player.in_round(decision_chosen).tomorrow_low,
            "round": decision_chosen,
            "today_chosen": player.in_round(decision_chosen).today - player.in_round(decision_chosen).savings,
            "tmr_high_chosen": player.in_round(decision_chosen).tomorrow_high + player.in_round(decision_chosen).savings,
            "tmr_low_chosen": player.in_round(decision_chosen).tomorrow_low + player.in_round(decision_chosen).savings,
            "savings_chosen": player.in_round(decision_chosen).savings,
            "period_generate": player.in_round(decision_chosen).period_chosen,
            "risky_generate": player.in_round(decision_chosen).risky_chosen,
        }
    def show_result(player: Player):
            if player.period_chosen == 1:
                print("The computer selected Period 1")
            else:
                if player.risky_chosen==1:
                    print("The computer selected Period 2 and high return")
                else:
                    print("The computer selected Period 2 and low return")


page_sequence = [InvestmentDecision, Results]
