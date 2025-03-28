# %%
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

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

# %%



#df = pd.read_csv('../dataset/GOOG-year.csv')
#df.head()

# %%
    count = int(np.ceil(len(df) * 0.1))
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0
    signals['trend'] = df['Close']
    signals['RollingMax'] = (signals.trend.shift(1).rolling(count).max())
    signals['RollingMin'] = (signals.trend.shift(1).rolling(count).min())
    signals.loc[signals['RollingMax'] < signals.trend, 'signal'] = -1
    signals.loc[signals['RollingMin'] > signals.trend, 'signal'] = 1
    signals

    # %%
    def buy_stock(
        real_movement,
        signal,
        initial_money = 10000,
        max_buy = 1,
        max_sell = 1,
    ):
        """
        real_movement = actual movement in the real world
        delay = how much interval you want to delay to change our decision from buy to sell, vice versa
        initial_state = 1 is buy, 0 is sell
        initial_money = 1000, ignore what kind of currency
        max_buy = max quantity for share to buy
        max_sell = max quantity for share to sell
        """
        starting_money = initial_money
        states_sell = []
        states_buy = []
        current_inventory = 0
        days = 0

        def buy(i, initial_money, current_inventory):
            shares = initial_money // real_movement[i]
            if shares < 1:
                print(
                    'day %d: total balances %f, not enough money to buy a unit price %f'
                    % (i, initial_money, real_movement[i])
                )
            else:
                if shares > max_buy:
                    buy_units = max_buy
                else:
                    buy_units = shares
                initial_money -= buy_units * real_movement[i]
                current_inventory += buy_units
                print(
                    'day %d: buy %d units at price %f, total balance %f'
                    % (i, buy_units, buy_units * real_movement[i], initial_money)
                )
                states_buy.append(0)
            return initial_money, current_inventory

        for i in range(real_movement.shape[0] - int(0.025 * len(df))):
            state = signal[i]
            days += 1
            if state == 1:
                initial_money, current_inventory = buy(
                    i, initial_money, current_inventory
                )
                states_buy.append(i)
            elif state == -1:
                if current_inventory == 0:
                        print('day %d: cannot sell anything, inventory 0' % (i))
                else:
                    if current_inventory > max_sell:
                        sell_units = max_sell
                    else:
                        sell_units = current_inventory
                    current_inventory -= sell_units
                    total_sell = sell_units * real_movement[i]
                    initial_money += total_sell
                    try:
                        invest = (
                            (real_movement[i] - real_movement[states_buy[-1]])
                            / real_movement[states_buy[-1]]
                        ) * 100
                    except:
                        invest = 0
                    print(
                        'day %d, sell %d units at price %f, investment %f %%, total balance %f,'
                        % (i, sell_units, total_sell, invest, initial_money)
                    )
                states_sell.append(i)
                
        invest = ((initial_money - starting_money) / starting_money) * 100
        total_gains = initial_money - starting_money
        return states_buy, states_sell, total_gains, invest, days

    # %%
    states_buy, states_sell, total_gains, invest, days = buy_stock(df.Close, signals['signal'])

    # %%
    close = df['Close']
    fig = plt.figure(figsize = (15,5))
    plt.plot(close, color='r', lw=2.)
    plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
    plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
    plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
    plt.legend()
    #plt.show()

    # %%
    return states_buy, states_sell, total_gains, invest, days



