# %%
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
import random
sns.set()

# %%
import pkg_resources
import types

import schedule
from datetime import datetime, timedelta

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def trial(): 
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

    # # %%
    # df = pd.read_csv('../dataset/GOOG-year.csv')
    # df.head()

    import yfinance as yf
    import pandas as pd

    days_ago = datetime.now() - timedelta(days=45)
    df = yf.download("GOOG", start=days_ago, end=datetime.now(), interval='1h')

    # %%


    # %%
    class Deep_Evolution_Strategy:

        inputs = None

        def __init__(
            self, weights, reward_function, population_size, sigma, learning_rate
        ):
            self.weights = weights
            self.reward_function = reward_function
            self.population_size = population_size
            self.sigma = sigma
            self.learning_rate = learning_rate

        def _get_weight_from_population(self, weights, population):
            weights_population = []
            for index, i in enumerate(population):
                jittered = self.sigma * i
                weights_population.append(weights[index] + jittered)
            return weights_population

        def get_weights(self):
            return self.weights

        def train(self, epoch = 100, print_every = 1):
            lasttime = time.time()
            for i in range(epoch):
                population = []
                rewards = np.zeros(self.population_size)
                for k in range(self.population_size):
                    x = []
                    for w in self.weights:
                        x.append(np.random.randn(*w.shape))
                    population.append(x)
                for k in range(self.population_size):
                    weights_population = self._get_weight_from_population(
                        self.weights, population[k]
                    )
                    rewards[k] = self.reward_function(weights_population)
                rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-7)
                for index, w in enumerate(self.weights):
                    A = np.array([p[index] for p in population])
                    self.weights[index] = (
                        w
                        + self.learning_rate
                        / (self.population_size * self.sigma)
                        * np.dot(A.T, rewards).T
                    )
                if (i + 1) % print_every == 0:
                    print(
                        'iter %d. reward: %f'
                        % (i + 1, self.reward_function(self.weights))
                    )
            print('time taken to train:', time.time() - lasttime, 'seconds')


    class Model:
        def __init__(self, input_size, layer_size, output_size):
            self.weights = [
                np.random.randn(input_size, layer_size),
                np.random.randn(layer_size, output_size),
                np.random.randn(1, layer_size),
            ]

        def predict(self, inputs):
            feed = np.dot(inputs, self.weights[0]) + self.weights[-1]
            decision = np.dot(feed, self.weights[1])
            return decision

        def get_weights(self):
            return self.weights

        def set_weights(self, weights):
            self.weights = weights

    # %%
    class Agent:

        POPULATION_SIZE = 15
        SIGMA = 0.1
        LEARNING_RATE = 0.03

        def __init__(self, model, window_size, trend, skip, initial_money):
            self.model = model
            self.window_size = window_size
            self.half_window = window_size // 2
            self.trend = trend
            self.skip = skip
            self.initial_money = initial_money
            self.es = Deep_Evolution_Strategy(
                self.model.get_weights(),
                self.get_reward,
                self.POPULATION_SIZE,
                self.SIGMA,
                self.LEARNING_RATE,
            )

        def act(self, sequence):
            decision = self.model.predict(np.array(sequence))
            return np.argmax(decision[0])
        
        def get_state(self, t):
            window_size = self.window_size + 1
            d = t - window_size + 1
            block = self.trend[d : t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0 : t + 1]
            res = []
            for i in range(window_size - 1):
                res.append(block[i + 1] - block[i])
            return np.array([res])

        def get_reward(self, weights):
            initial_money = self.initial_money
            starting_money = initial_money
            self.model.weights = weights
            state = self.get_state(0)
            inventory = []
            quantity = 0
            for t in range(0, len(self.trend) - 1, self.skip):
                action = self.act(state)
                next_state = self.get_state(t + 1)
                
                if action == 1 and starting_money >= self.trend[t]:
                    inventory.append(self.trend[t])
                    starting_money -= close[t]
                    
                elif action == 2 and len(inventory):
                    bought_price = inventory.pop(0)
                    starting_money += self.trend[t]

                state = next_state
            return ((starting_money - initial_money) / initial_money) * 100

        def fit(self, iterations, checkpoint):
            self.es.train(iterations, print_every = checkpoint)

        def buy(self):
            initial_money = self.initial_money
            state = self.get_state(0)
            starting_money = initial_money
            states_sell = []
            states_buy = []
            inventory = []
            days = 0
            for t in range(0, len(self.trend) - 1, self.skip):
                action = self.act(state)
                next_state = self.get_state(t + 1)
                days += 1
                if action == 1 and initial_money >= self.trend[t]:
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
            return states_buy, states_sell, total_gains, invest, state, days

    # %%
    close = df.Close.values.tolist()
    window_size = 30
    skip = 1
    initial_money = 10000

    model = Model(input_size = window_size, layer_size = 500, output_size = 3)
    agent = Agent(model = model, 
                window_size = window_size,
                trend = close,
                skip = skip,
                initial_money = initial_money)
    agent.fit(iterations = 500, checkpoint = 10)

    # %%
    states_buy, states_sell, total_gains, invest, state, days = agent.buy()
    print("States buy: {}".format(states_buy))
    print("States sell: {}".format(states_sell))
    print("State: {}".format(state))
    print("Days: {}".format(days))
    print("Cool")
    API_KEY = "PK8JAI6R51F7SC86GT4L"
    SECRET_KEY = "vIOxUHOwrVZve7kDfnEvijBrQg9cKcoPUedgAqJY"

    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)


    # # Getting account information and printing it
    # account = trading_client.get_account()
    # for property_name, value in account:
    #   print(f"\"{property_name}\": {value}")

    # Setting parameters for our buy order
    market_order_data_buy = MarketOrderRequest(
                        symbol="GOOG",
                        qty=1,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.GTC
                    )
    market_order_data_sell = MarketOrderRequest(
                        symbol="GOOG",
                        qty=1,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC
                    )

    # Submitting the order and then printing the returned object
    for buy in states_buy:
        if buy > days - 2:
            market_order = trading_client.submit_order(market_order_data_buy)
            for property_name, value in market_order:
                print(f"\"{property_name}\": {value}")
    for sell in states_sell:
        if sell > days - 2:
            market_order = trading_client.submit_order(market_order_data_sell)
            for property_name, value in market_order:
                print(f"\"{property_name}\": {value}")
    

    # %%
    fig = plt.figure(figsize = (15,5))
    plt.plot(close, color='r', lw=2.)
    plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
    plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
    plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
    plt.legend()
    #plt.show()

    # %%
# Schedule the execution to start at 9:30 AM
start_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
current_time = datetime.now()

# If the current time is past 9:30 AM, schedule the first execution for the next day
# if current_time > start_time:
#     start_time += timedelta(days=1)

# Calculate the time difference in seconds between the current time and the scheduled start time
time_difference_start = (start_time - current_time).total_seconds()

# Calculate the time difference in seconds between the current time and 4 PM
end_time = current_time.replace(hour=23, minute=0, second=0, microsecond=0)
time_difference_end = (end_time - current_time).total_seconds()

# Wait until the scheduled start time
#time.sleep(time_difference_start)

# Run the code every 15 minutes until 4 PM
while current_time <= end_time:
    trial()
    time.sleep(900)  # 900 seconds = 15 minutes
    current_time = datetime.now()


print("Execution has been completed.")


