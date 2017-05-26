from numpy import random
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

# 2 keepers 5 defenders 5 mid 3 fwd
def run():
    players = Pool()
    population_size = 100
    data = DataAccess()
    rows = data.get_gameweeks(1, 38)

    for row in rows:
        players.add(row)
    print("A total of {} players read from the database".format(players.count()))
    gen = []
    count = 0
    while(count < population_size):
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
            gen.append(chromosome)
            count += 1

    avg, highest, lowest = [], [], []
    for i in range(0, 100):
        print("Starting generation {}".format(i))
        gen, gen_h, gen_l, gen_a = get_generation(gen, population_size, players)
        avg.append(gen_a)
        highest.append(gen_h)
        lowest.append(gen_l)

    plt.plot(list(range(0,100)), highest)
    plt.plot(list(range(0,100)), avg)
    plt.plot(list(range(0,100)), lowest)
    plt.plot(list(range(0,100)), list(2245.47 for i in range(0, 100)), '-')
    plt.legend(['Highest', 'Average', 'Lowest', 'Avg Participant'], loc='lower right')
    plt.ylabel('Score')
    plt.xlabel('Generation')
    plt.show()
    return gen

def elitism(pool):
    participants = sorted(pool, key=lambda team: team.get_score())
    return participants[0]

def selection(pool):
   total = sum(c.get_score() for c in pool)
   r = random.uniform(0, total)
   upto = 0
   for c in pool:
      if upto + c.get_score() >= r:
         return c
      upto += c.get_score()

def tournament_selection(pool, size):
    participants = []
    while(len(participants) < size):
        temp = selection(pool)
        # if not(temp in participants):
        participants.append(temp)
    participants = sorted(participants, key=lambda team: team.get_score())
    return participants[0]

def crossover(p1, p2, pc):
    originals = [p1.alleles, p2.alleles]

    if random.random() < pc:
        point = random.randint(0, len(p1.alleles) - 1)
        for i in range(point, len(p1.alleles)):
            tmp = p2.alleles[i]
            p2.swap(p1.alleles[i], i)
            p1.swap(tmp, i)

def uniform_crossover(p1, p2, pc):
    originals = [p1.alleles, p2.alleles]

    for i in range(0, len(p1.alleles)):
        if random.random() < pc:
            tmp = p1.alleles[i]
            p2.swap(p1.alleles[i], i)
            p1.swap(tmp, i)

def mutation(chromosome, players, pm):
    for i in range(0, len(chromosome.alleles)):
        if random.random() < pm:
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


def get_generation(pool, number, players):
    crossover_rate = 0.2
    mutation_rate = 0.05

    highest, avg, lowest =  0, 0, 10000

    new_pool = []

    while(len(new_pool) < number):
        # Select both parents
        parent1 = selection(pool)

        while True:
            parent2 = selection(pool, )
            if parent1 != parent2:
                break
        # print('= Parent 1 {} ='.format(parent1.get_score()))
        # print_chromosome(parent1.alleles)
        # print('= Parent 2 {} ='.format(parent2.get_score()))
        # print_chromosome(parent2.alleles)
        # print('=========\n\n')

        # Perform crossover
        uniform_crossover(parent1, parent2, crossover_rate)
        # print('= Parent 1 After Cross {} ='.format(parent1.get_score()))
        # print_chromosome(parent1.alleles)
        # print('= Parent 2 After Cross {} ='.format(parent2.get_score()))
        # print_chromosome(parent2.alleles)
        # print('=========\n')

        # perform mutation
        mutation(parent1, players, mutation_rate)
        mutation(parent2, players, mutation_rate)
        # print('= Parent 1 After Mut {} ='.format(parent1.get_score()))
        # print_chromosome(parent1.alleles)
        # print('= Parent 2 After Mut {} ='.format(parent2.get_score()))
        # print_chromosome(parent2.alleles)
        # print('=========\n')

        # Keep track of the highest, lowest and total
        p1_score = parent1.get_final_score()
        p2_score = parent2.get_final_score()

        if(p1_score > highest):
            highest = p1_score
        if(p1_score < lowest):
            lowest = p1_score
        if(p2_score > highest):
            highest = p2_score
        if(p2_score < lowest):
            lowest = p2_score
        avg += p1_score + p2_score

        # Add both elements to the new pool
        new_pool.append(parent1)
        new_pool.append(parent2)

    avg = avg/len(new_pool)
    return new_pool, highest, lowest, avg

def print_chromosome(array):
    for p in array:
        print(p.name)

def main():
    byScore = []
    byPrice = []

    for i in range(0, 1):
        print("Starting run {}".format(i))
        gen = run()

        byScore.append(sorted(gen, key=lambda team: team.get_score())[len(gen)-1])
        byPrice.append(sorted(gen, key=lambda team: team.get_price())[len(gen)-1])
    byScore = sorted(byScore, key=lambda team: team.get_score())
    byPrice = sorted(byPrice, key=lambda team: team.get_price())
    print("Team with top score - Score: {} Vale: ${} Final Score: {}".format(byScore[len(byScore)-1].get_score(), byScore[len(byScore)-1].get_price(), byScore[len(byScore)-1].get_final_score()))
    print("======")
    print_chromosome(byScore[len(byScore)-1].alleles)
    print("======")

    print("Team with highest price - Score: {} Vale: ${} Final Score: {}".format(byPrice[len(byScore)-1].get_score(), byPrice[len(byScore)-1].get_price(), byScore[len(byScore)-1].get_final_score()))
    print("======")
    print_chromosome(byPrice[len(byScore)-1].alleles)
    print("======")

main()
