"""my_team.py

Champlain College CSI-480, Fall 2017
The following code was adapted by Joshua Auerbach (jauerbach@champlain.edu)
from the UC Berkeley Pacman Projects (see license and attribution below).

----------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

from capture_agents import CaptureAgent
import random
import time
import util
from game import Directions
import game

#################
# Team creation #
#################

def create_team(first_index, second_index, is_red,
               first='Top', second='Bottom'):
    """
    This function should return a list of two agents that will form the
    team, initialized using first_index and second_index as their agent
    index numbers.  is_red is True if the red team is being created, and
    will be False if the blue team is being created.

    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --red_opts and --blue_opts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(first_index), eval(second)(second_index)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baseline_team.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def register_initial_state(self, game_state):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distance_calculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.get_distance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.register_initial_state in capture_agents.py.
        '''
        CaptureAgent.register_initial_state(self, game_state)

        '''
        Your initialization code goes here, if you need any.
        '''
        self.behaviour_state = 'guard'
        self.set_center(game_state)
        self.eaten_food = 0
        self.prev_food_state = self.get_food_you_are_defending(game_state)
        self.opponent_indices = self.get_opponents(game_state)
        self.team_indices = self.get_team(game_state)
        
        self.teammate_index = self.get_team(game_state)[:]
        self.teammate_index.remove(self.index)

        self.defence_destination = None
        self.attack_destination = None
        self.opponent_positions = {}
        self.opponent_prev_positions = {}
        self.opponent_detected = None
        for opponent_index in self.opponent_indices:
            self.opponent_positions[opponent_index] = None
            self.opponent_prev_positions[opponent_index] = None

    def update_defence_destination(self, game_state):
        if self.destination_reached(game_state, self.defence_destination):
            self.defence_destination = self.opponent_detected
        else:
            if self.opponent_detected != None:
                self.defence_destination = self.opponent_detected
            else:
                if self.defence_destination == None:
                    return
                elif not self.in_home_territory(game_state, self.defence_destination, 0):
                    self.defence_destination = None
                else:
                    return

    def update_opponent_detected(self, game_state):
        opponent_positions = self.get_opponent_positions_list(game_state)
        food_eaten_by_opponent = self.food_eaten_by_opponent(game_state)
        if len(opponent_positions) < 2 and len(food_eaten_by_opponent) > 0:
            if len(opponent_positions) == 0:
                opponent_positions = food_eaten_by_opponent
            else:
                for op_eat_food in food_eaten_by_opponent:
                    for opponent_position in opponent_positions:
                        if self.get_maze_distance(op_eat_food, opponent_position) > 1:
                            opponent_positions = opponent_positions + [op_eat_food]
        if len(opponent_positions) == 1:
            if self.closest_team_member(game_state, opponent_position[0])[0] == self.index:
                self.opponent_detected = opponent_position[0]
                return
            else:
                self.opponent_detected = None
                return
        elif len(opponent_positions) > 1:
            min_distance= 9999999999
            for position in opponent_positions:
                index, distance = self.closest_team_member(game_state, position)
                if distance < min_distance:
                    min_distance = distance
                    min_position = position
                    min_index = index
                if min_index == self.index:
                    self.opponent_detected = min_position
                    return
                else:
                    for position in opponent_positions:
                        if not position == min_position:
                            self.opponent_detected = position
                            return
        else:
            self.opponent_detected = None

    def update_opponent_positions(self, game_state):
        self.opponent_prev_positions = self.opponent_positions.copy()
        self.opponent_positions = self.get_opponent_positions_dict(game_state)

    def get_opponent_positions_dict(self, game_state):
        opponent_positions_dict = {}
        for index in self.opponent_indices:
            opponent_positions_dict[index] = game_state.get_agent_position(index)
        return opponent_positions_dict

    def get_opponent_positions_list(self, game_state):
        opponent_positions_list = []
        for index in self.opponent_indices:
            if not game_state.get_agent_position(index) == None:
                opponent_positions_list = opponent_positions_list + [game_state.get_agent_position(index)]
        return opponent_positions_list

    def destination_reached(self, game_state, destination):
        if destination == None:
            return False
        return self.get_maze_distance(game_state.get_agent_position(self.index), destination) == 0

    def killed_opponent(self, game_state, index):
        for opponent_index in self.opponent_indices:
            if self.opponent_positions[opponent_index] == game_state.get_initial_agent_position(opponent_index):
                return True
            elif not self.opponent_prev_positions[opponent_index] == None:
                if self.opponent_positions[opponent_index] == None and util.manhattan_distance(game_state.get_agent_position(index), self.opponent_prev_positions[oppoent_index]) < 2:
                    return True
        return False

    def opponent_is_dead(self, game_state):
        for team_index in self.team_indices:
            if self.killed_opponent(game_state, team_index):
                return True
        return False

    def should_i_attack(self, game_state):
        min_distance = 99999999999
        min_team_index = None
        if self.opponent_is_dead(game_state):
            for opponent_index in self.opponent_indices:
                opponent_position = game_state.get_agent_position(opponent_index)
                if opponent_position != None:
                    team_index, distance = self.closest_team_member(game_state, opponent_position)
                    if distance < min_distance:
                        min_distance = distance
                        min_team_index = team_index
        else:
            return False
        if min_team_index == None:
            return self.index == min(self.team_indices)
        elif(self.index) != min_team_index:
            return True
        return False

    def is_dead(self, game_state):
        if self.get_maze_distance(game_state.get_agent_position(self.index), game_state.get_initial_agent_position(self.index)) <= 2:
            return True
        return False

    def too_much_food(self):
        if self.eaten_food > 3:
            return True
        return False

    def reset_food_count(self):
        self.eaten_food = 0

    def next_behaviour_state(self, game_state):
        self.update_opponent_positions(game_state)
        self.update_opponent_detected(game_state)
        self.update_defence_destination(game_state)
        if game_state.get_agent_state(self.index).scared_timer > 10:
            self.behaviour_state = 'offence'

        elif self.behaviour_state == 'guard':
            if not self.defence_destination == None:
                self.behaviour_state = 'defence'
            elif self.should_i_attack(game_state):
                self.behaviour_state = 'offence'
            return
        elif self.behaviour_state == 'defence':
            if game_state.get_agent_state(self.index).is_pacman:
                self.behaviour_state = 'flee'
            elif self.should_i_attack(game_state):
                self.behaviour_state = 'offence'
            elif self.defence_destination == None:
                self.behaviour_state = 'guard'
            return

        elif self.behaviour_state == 'offence':
            if self.too_much_food() or (self.nearest_ghost_distance(game_state) <= 3 and game_state.get_agent_state(self.index).is_pacman):
                self.behaviour_state = 'flee'
            elif not self.defence_destination == None:
                self.behaviour_state = 'defence'
            elif self.is_dead(game_state):
                self.reset_food_count()
                self.behaviour_state = 'guard'
            return

        elif self.behaviour_state == 'flee':
            if self.in_home_territory(game_state, game_state.get_agent_position(self.index), 0) or self.is_dead(game_state):
                sekf,reset_food_count()
                self.behaviour_state = 'guard'
            return
        
        else:
            self.update_opponent_positions(game_state)
            self.behaviour_state = 'gaurd'


    def choose_action(self, game_state):
        """
        Picks among actions randomly.
        """
        self.next_behaviour_state(game_state)
        if self.behaviour_state == 'gaurd':
            print('@AYBOY@')#return self.choose_flee_action(game_state)return self.choose_guard_action(game_state)
        elif self.behaviour_state == 'defence':
            print('@AYBOY@')#return self.choose_flee_action(game_state)return self.choose_defensive_action(game_state)
        elif self.behaviour_state == 'offence':
            print('@AYBOY@')#return self.choose_flee_action(game_state)return self.choose_offensive_action(game_state)
        elif self.behaviour_state == 'flee':
            print('@AYBOY@')#return self.choose_flee_action(game_state)
        else:
            return Directions.STOP

    def get_successor(self, game_state, action):
        successor = game_state.generate_successor(self.index, action)
        pos = successor.get_agent_state(self.index).get_position()
        if pos != util.nearest_point(pos):
            return successor.generate_successor(self.index, action)
        return successor


    def closest_teammember(self,game_state, position):
        min_distance = 999999
        for index in self.team_indices:
            distance = self.get_maze_distance(game_state.get_agent_position(index, position))
            if distance < min_distance:
                min_distance = distance
                min_index = index
        return min_index, min_distance





    def food_eaten_by_opponent(self, game_state):
        food_eaten_by_opponent = []
        for x in range(game_state.get_walls().width):
          for y in range(game_state.get_walls().height):
            if self.prev_food_state[x][y] == True and self.get_food_you_are_defending(game_state)[x][y] == False and self.in_home__territory(game_state, (x,y), 0):
              food_eaten_by_opponent = food_eaten_by_Opponent + [(x,y)]
        self.prev_food_state = self.get_food_you_are_defending(game_state)
        return food_eaten_by_opponent



class Top(DummyAgent):

    def set_center(self, game_state):
        '''
        x = game_state.get_walls().width/2
        offset = 1
        if self.red:
            x = x - (1 + offset)
        else:
            x = x + offset
        y = game_state.get_walls().height/2
        y_max = game_state.get_walls().height
        y_center = int(round(y_max/4*3))
        for i in range(0,y_max):
            y_candidate = y_center + i
            if y_candidate <= y_max and y_candidate > 0:
                if not game_state.has_wall(x, y_candidate):
                    break
            y_candidate = y_center - i
            if y_candidate <= y_max and y_candidate > 0:
                if not game_state.has_wall(x, y_candidate):
                    break
        self.center = (x, y_candidate)
        '''
        self.center = (10,10)

class Bottom(DummyAgent):

    def set_center(self, game_state):
        '''
        x = game_state.get_walls().width/2
        offset = 1
        if self.red:
            x = x - (1 + offset)
        else:
            x = x + offset
        y = game_state.get_walls().height/2
        y_max = game_state.get_walls().height
        y_center = int(round(y_max/4))
        for i in range(0,y_max):
            y_candidate = y_center + i
            if y_candidate <= y_max and y_candidate > 0:
                if not game_state.has_wall(x, y_candidate):
                    break
            y_candidate = y_center - i
            if y_candidate <= y_max and y_candidate > 0:
                if not game_state.has_wall(x, y_candidate):
                    break
        self.center = (x, y_candidate)
        '''
        self.center = (10,10)