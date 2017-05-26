from numpy import random
import copy
import matplotlib.pyplot as plt
from data_access import DataAccess
import csv

class Chromosome:
    def __init__(self):
	# Each player is inserted as an allele
        self.alleles = []

    def get_price(self):
	# Obtain the price of the current team
        price = sum(float(i.price) for i in self.alleles)
        return price

    def get_score(self):
	# Calculate the chromosomes fitness
        score = sum(int(i.points) for i in self.alleles)
        return score

    def get_final_score(self):
	# Calculate the "projected" score for the chromosome
        score = sum(int(i.final_points) for i in self.alleles)
        return score

    def swap(self, player, position):
	# Exchange an existing player with a new one
        valid = True
        tmp = self.alleles[position]
        self.alleles[position] = player
	# Make sure that the newly generated chromosome
	# Is still a valid one
        if not(self.is_valid()):
            self.alleles[position] = tmp
            valid = False
        return valid

    def is_valid(self):
    	# Verify that the chromsome currently
    	# contains a valid structure
        player_ids = {}
        if(self.get_price() <= 105):
            teams = {}
            for p in self.alleles:
                if(p.id in player_ids):
                    return False
                else:
                    player_ids[p.id] = 1

                if(p.team in teams):
                    if teams[p.team] == 2:
                        return False
                    else:
                        teams[p.team] += 1
                else:
                    teams[p.team] = 1
            return True
        else:
            return False

class Pool:
    def __init__(self):
        self.keepers = []
        self.defenders = []
        self.midfielders = []
        self.attackers = []

    def count(self):
        return len(self.keepers) + len(self.defenders) + len(self.midfielders) + len(self.attackers)

    def add(self, row):
        if row['position'] == 'Goalkeeper':
            sel_pool = self.keepers
        elif row['position'] == 'Defender':
            sel_pool = self.defenders
        elif row['position'] == 'Midfielder':
            sel_pool = self.midfielders
        else:
            sel_pool = self.attackers

        try:
            oldPlayer = next(x for x in sel_pool if row['epl_player_system_id'] == x.id)
            if(row['gameweek'] > 19):
                oldPlayer.final_points += row['points']
            else:
                oldPlayer.final_points += row['points']
                oldPlayer.points += row['points']

            if(row['gameweek'] > oldPlayer.gameweek):
                oldPlayer.gameweek = row['gameweek']
                oldPlayer.price = row['value']

        except StopIteration:
            newPlayer = Player(row)
            sel_pool.append(newPlayer)

class Player:
    def __init__(self, row):
        self.id = row['epl_player_system_id']
        self.team = row['epl_team_name']
        self.position = row['position']
        self.gameweek = row['gameweek']
        self.price = row['value']
        self.points = 0
        self.final_points = 0
        self.name = row['name']

        if(self.gameweek > 19):
            self.final_points += row['points']
        else:
            self.points += row['points']
            self.final_points += row['points']

    def get_score(self):
        return self.points

def weighted_choice(choices):
   total = sum(c.get_score() for c in choices)
   r = random.uniform(0, total)
   upto = 0
   for c in choices:
      if upto + c.get_score() >= r:
         return c
      upto += c.get_score()

def pick_players(chromosome_array, pool, number):
    for i in range(0, number):
        player = weighted_choice(pool)
        while(player in chromosome_array):
            player = weighted_choice(pool)
        chromosome_array.append(player)

def acceptanceProbability(energy, newEnergy, temperature):
    if(newEnergy > energy):
        return 1.0
    else:
        return ((energy - newEnergy)/temperature)

# 2 keepers 5 defenders 5 mid 3 fwd
def run():
    players = Pool()
    population_size = 100
    data = DataAccess()
    rows = data.get_gameweeks(1, 38)

    for row in rows:
        players.add(row)
    print("A total of {} players read from the database".format(players.count()))

    while(True):
        chromosome = Chromosome()
        # Pick goalkeepers
        pick_players(chromosome.alleles, players.keepers, 2)
        # Pick defenders
        pick_players(chromosome.alleles, players.defenders, 5)
        # Pick midfielders
        pick_players(chromosome.alleles, players.midfielders, 5)
        # Pick attackers
        pick_players(chromosome.alleles, players.attackers, 3)
        # Append to generation if team is approved
        if chromosome.is_valid():
            break

    current_score = chromosome.get_score()
    temp = 5000
    cooling_rate = 0.003
    mutation_rate = 0.05
    best = copy.deepcopy(chromosome)
    x = []
    y = []
    final = []
    while(temp > 1):
        neighbor = copy.deepcopy(chromosome)
        mutation(neighbor, players)

        p = acceptanceProbability(chromosome.get_score(), neighbor.get_score(), temp)
        if(p > random.random()):
            chromosome = neighbor

        if(chromosome.get_score() > best.get_score()):
            best = copy.deepcopy(chromosome)

        x.append(5000 - temp)
        y.append(chromosome.get_final_score())

        temp *= 1-cooling_rate

    plt.plot(x, y)

    plt.xlabel('Temperature')
    plt.ylabel('Score')
    plt.plot(x, list(2245.47 for i in range(0, len(y))), '-')
    plt.gca().invert_xaxis()
    plt.legend(['Simulated Annealing', 'Avg Participant'], loc='lower right')
    plt.show()

    print(best.get_score())
    print_chromosome(best.alleles)

def mutation(chromosome, players):
    i = random.randint(len(chromosome.alleles))
    if chromosome.alleles[i].position == 'Goalkeeper':
        pool = players.keepers
    elif chromosome.alleles[i].position == 'Defender':
        pool = players.defenders
    elif chromosome.alleles[i].position == 'Midfielder':
        pool = players.midfielders
    else:
        pool = players.attackers
    while True:
        new_player = weighted_choice(pool)
        if not(new_player in chromosome.alleles):
            valid = chromosome.swap(new_player, i)
            if valid:
                break

def print_chromosome(array):
    for p in array:
        print(p.name)

def main():
    run()
main()
