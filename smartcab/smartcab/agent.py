import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import pandas as pd
import numpy as np

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {}
        self.alpha = 0.9
        self.gamma = 0.33
        self.epsilon = 0.1
        self.net_reward = 0
        self.succ=0
        self.t_total =0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.p_state = None
        self.p_action = None
        self.p_reward = None
        self.p_net_reward = 0
        self.net_reward = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        # TODO: Update state
        inputs['waypoint'] = self.next_waypoint
        inputs['deadline'] = deadline

        #del inputs['left']
        del inputs['right']
        #del inputs['oncoming']
        self.state = tuple(sorted(inputs.items()))

        # TODO: Select action according to your policy
        action = ""
        #action = random.choice(self.Environment.valid_actions)
        Qval, action = self.pickQact(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.p_state != None:
            if (self.p_state, self.p_action) not in self.Q:
                self.Q[(self.p_state, self.p_action)] = 0

            self.Q[(self.p_state, self.p_action)] = (1-self.alpha) * self.Q[(self.p_state, self.p_action)] + self.alpha*(self.p_reward + self.gamma * self.pickQact(self.state)[0]) 


        
        if self.env.done:
            self.succ += 1

        #self.t_total += t
          
        #Setting current parameters as previous parameters
        self.p_state = self.state
        self.p_action = action
        self.p_reward = reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, time = {}, success = {}".format(deadline, inputs, action, reward, t, self.succ)  # [debug]

    #Checks if a Q value exists in the Q matrix for the given (state, action) pair     
    def getQval(self, state, action):
        if (state, action) not in self.Q:
            self.Q[(state, action)] = 0
        return self.Q[(state,action)]   

    def pickQact(self, state):
         b_action = random.choice(Environment.valid_actions)
         if self.epsilon > random.random():
            maxQ = self.getQval(state, b_action)
         else:
            maxQ = -999999999
            for a in Environment.valid_actions:
                q = self.getQval(state, a)
                if q > maxQ:
                    maxQ = q
                    b_action = a
                elif q==maxQ:
                    if self.epsilon > random.random():
                        b_action = a

         return (maxQ, b_action) 




def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
