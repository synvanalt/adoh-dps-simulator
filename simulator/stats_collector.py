

class StatsCollector:
    def __init__(self):
        self.attempts_made = 0
        self.hits = 0
        self.crit_hits = 0
        self.legend_procs = 0
        self.hit_rate = 0.0
        self.crit_hit_rate = 0.0
        self.legend_proc_rate = 0.0
        self.attempts_made_per_attack = []
        self.hits_per_attack = []
        self.crits_per_attack = []

    def init_zeroes_lists(self, list_length):
        self.attempts_made_per_attack = [0] * list_length
        self.hits_per_attack = [0] * list_length
        self.crits_per_attack = [0] * list_length

    def calc_rates_percentages(self):
        if self.attempts_made == 0 or self.hits == 0:
            return  # Avoid division by zero

        self.legend_proc_rate = round((self.legend_procs / self.hits) * 100, 2)
        self.crit_hit_rate = round((self.crit_hits / self.attempts_made) * 100, 2)
        self.hit_rate = round((self.hits / self.attempts_made) * 100, 2)

        for i in range(len(self.attempts_made_per_attack)):
            self.crits_per_attack[i] = round((self.crits_per_attack[i] / self.attempts_made_per_attack[i]) * 100, 1)
            self.hits_per_attack[i] = round((self.hits_per_attack[i] / self.attempts_made_per_attack[i]) * 100, 1)
