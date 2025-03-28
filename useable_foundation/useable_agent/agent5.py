# %%
import numpy as np
import pandas as pd
import time
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()



# %%
#df = pd.read_csv('../dataset/GOOG-year.csv')
#df.head()

# %%
from collections import deque
import random

import pkg_resources
import types

def step(df):
    def get_imports():
        for name, val in globals().items():
            if isinstance(val, types.ModuleType):
                name = val.__name__.split('.')[0]
            elif isinstance(val, type):
                name = val.__module__.split('.')[0]
            poorly_named_packages = {'PIL': 'Pillow', 'sklearn': 'scikit-learn'}
            if name in poorly_named_packages.keys():
                name = poorly_named_packages[name]
            yield name


    imports = list(set(get_imports()))
    requirements = []
    for m in pkg_resources.working_set:
        if m.project_name in imports and m.project_name != 'pip':
            requirements.append((m.project_name, m.version))

    for r in requirements:
        print('{}=={}'.format(*r))


    class Agent:
        def __init__(self, state_size, window_size, trend, skip, batch_size):
            self.state_size = state_size
            self.window_size = window_size
            self.half_window = window_size // 2
            self.trend = trend
            self.skip = skip
            self.action_size = 3
            self.batch_size = batch_size
            self.memory = deque(maxlen = 1000)
            self.inventory = []

            self.gamma = 0.95
            self.epsilon = 0.5
            self.epsilon_min = 0.01
            self.epsilon_decay = 0.999

            tf.compat.v1.reset_default_graph()
            self.sess = tf.compat.v1.InteractiveSession()
            tf.compat.v1.disable_eager_execution()
            self.X = tf.compat.v1.placeholder(tf.float32, [None, self.state_size])
            self.Y = tf.compat.v1.placeholder(tf.float32, [None, self.action_size])
            feed = tf.compat.v1.layers.dense(self.X, 256, activation = tf.nn.relu)
            self.logits = tf.compat.v1.layers.dense(feed, self.action_size)
            self.cost = tf.reduce_mean(input_tensor=tf.square(self.Y - self.logits))
            self.optimizer = tf.compat.v1.train.GradientDescentOptimizer(1e-5).minimize(
                self.cost
            )
            self.sess.run(tf.compat.v1.global_variables_initializer())

        def act(self, state):
            if random.random() <= self.epsilon:
                return random.randrange(self.action_size)
            return np.argmax(
                self.sess.run(self.logits, feed_dict = {self.X: state})[0]
            )
        
        def get_state(self, t):
            window_size = self.window_size + 1
            d = t - window_size + 1
            block = self.trend[d : t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0 : t + 1]
            res = []
            for i in range(window_size - 1):
                res.append(block[i + 1] - block[i])
            return np.array([res])

        def replay(self, batch_size):
            mini_batch = []
            l = len(self.memory)
            for i in range(l - batch_size, l):
                mini_batch.append(self.memory[i])
            replay_size = len(mini_batch)
            X = np.empty((replay_size, self.state_size))
            Y = np.empty((replay_size, self.action_size))
            states = np.array([a[0][0] for a in mini_batch])
            new_states = np.array([a[3][0] for a in mini_batch])
            Q = self.sess.run(self.logits, feed_dict = {self.X: states})
            Q_new = self.sess.run(self.logits, feed_dict = {self.X: new_states})
            for i in range(len(mini_batch)):
                state, action, reward, next_state, done = mini_batch[i]
                target = Q[i]
                target[action] = reward
                if not done:
                    target[action] += self.gamma * np.amax(Q_new[i])
                X[i] = state
                Y[i] = target
            cost, _ = self.sess.run(
                [self.cost, self.optimizer], feed_dict = {self.X: X, self.Y: Y}
            )
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            return cost
        
        def buy(self, initial_money):
            starting_money = initial_money
            states_sell = []
            states_buy = []
            inventory = []
            state = self.get_state(0)
            days = 0
            for t in range(0, len(self.trend) - 1, self.skip):
                action = self.act(state)
                next_state = self.get_state(t + 1)
                days += 1
                
                if action == 1 and initial_money >= self.trend[t] and t < (len(self.trend) - self.half_window):
                    inventory.append(self.trend[t])
                    initial_money -= self.trend[t]
                    states_buy.append(t)
                    print('day %d: buy 1 unit at price %f, total balance %f'% (t, self.trend[t], initial_money))
                    
                    
                elif action == 2 and len(inventory):
                    bought_price = inventory.pop(0)
                    initial_money += self.trend[t]
                    states_sell.append(t)
                    try:
                        invest = ((close[t] - bought_price) / bought_price) * 100
                    except:
                        invest = 0
                    print(
                        'day %d, sell 1 unit at price %f, investment %f %%, total balance %f,'
                        % (t, close[t], invest, initial_money)
                    )
                
                state = next_state
            invest = ((initial_money - starting_money) / starting_money) * 100
            total_gains = initial_money - starting_money
            return states_buy, states_sell, total_gains, invest, days
            
        def train(self, iterations, checkpoint, initial_money):
            for i in range(iterations):
                total_profit = 0
                inventory = []
                state = self.get_state(0)
                starting_money = initial_money
                for t in range(0, len(self.trend) - 1, self.skip):
                    action = self.act(state)
                    next_state = self.get_state(t + 1)
                    
                    if action == 1 and starting_money >= self.trend[t] and t < (len(self.trend) - self.half_window):
                        inventory.append(self.trend[t])
                        starting_money -= self.trend[t]
                    
                    elif action == 2 and len(inventory) > 0:
                        bought_price = inventory.pop(0)
                        total_profit += self.trend[t] - bought_price
                        starting_money += self.trend[t]
                        
                    invest = ((starting_money - initial_money) / initial_money)
                    self.memory.append((state, action, invest, 
                                        next_state, starting_money < initial_money))
                    state = next_state
                    batch_size = min(self.batch_size, len(self.memory))
                    cost = self.replay(batch_size)
                if (i+1) % checkpoint == 0:
                    print('epoch: %d, total rewards: %f.3, cost: %f, total money: %f'%(i + 1, total_profit, cost,
                                                                                    starting_money))

    # %%
    close = df.Close.values.tolist()
    initial_money = 10000
    window_size = 30
    skip = 1
    batch_size = 32
    agent = Agent(state_size = window_size, 
                window_size = window_size, 
                trend = close, 
                skip = skip, 
                batch_size = batch_size)
    agent.train(iterations = 200, checkpoint = 10, initial_money = initial_money)

    # %%
    states_buy, states_sell, total_gains, invest, days = agent.buy(initial_money = initial_money)

    # %%
    fig = plt.figure(figsize = (15,5))
    plt.plot(close, color='r', lw=2.)
    plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
    plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
    plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
    plt.legend()
    plt.show()

# %%
    return states_buy, states_sell, total_gains, invest, days


