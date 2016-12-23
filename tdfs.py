import matplotlib.pyplot as plt
import numpy as np
import random

from arms import ArmBernoulli


#  UNIVERSE PARAMETERS
n_users = 3
n_arms = 5
t_horizon = 100

arm_means = [0.2, 0.3, 0.5, 0.8, 0.9]

arms = list()
for i in range(n_arms):
    arms.append(ArmBernoulli(arm_means[i]))

# ALGORITHM PARAMETERS


class SecondaryUser:
    ''' class used for user behaviour
    '''

    def __init__(self, n_arms, n_users):
        self.n_arms = n_arms
        self.n_users = n_users
        self.offset = random.randint(0, n_users - 1)
        self.rewards = np.zeros((n_arms, t_horizon))
        self.draws = np.zeros((n_arms, 1))
        self.collided_in_subsequence = False

    def decision(self, t):
        ''' Choses the arm to draw at each time step t.
            Args:
                - t (int): the time step.
            Output:
                - int: the index of the arm chosen by this user.
        '''
        if np.sum(self.draws > 0) < self.n_arms:
            # in this case we are still in initialization: we want all arms to
            # have been drawn at least once.
            return (t % self.n_arms) - self.offset
        else:
            # in this case we are in the main loop
            top_arm_to_consider = ((t - self.n_arms) % self.n_users) -\
                self.offset
            ucb_stat = np.sum(self.rewards, axis=1) / self.draws +\
                np.sqrt(log(t) / self.draws)
            arms_sorted = np.argsort(ucb_stat)
            return arms_sorted(top_arm_to_consider)


users = [SecondaryUser(n_arms, n_users) for i in range(n_users)]
total_rewards = np.zeros((t_horizon, 1))
choices = np.zeros(n_users)
for t in range(t_horizon):
    for (i, user) in enumerate(users):
        # each user makes its move
        choices[i] = user.decision(t)
    unique_choice, unique_count = np.unique(choices, return_counts=True)
    choice_count = dict(zip(unique_choice, unique_count))
    collisioned_users_id = (user_id for (user_id, choice) in enumerate(choices)
                            if choice_count[choice] > 1)
    for user_id in collisioned_users_id:
        users[user_id].collided_in_subsequence = True
    arms_to_draw = [choice for choice in choices if choice_count[choice] == 1]
    for (user_id, choice) in enumerate(choices):
        if choice in arms_to_draw:
            arm = arms[choice]
            user = users[user_id]
            reward = arm.draw()
            user.draws(choice) += 1
            user.rewards(choice, t) = reward
            total_rewards(t) += reward
    if (t == n_arms) or (t > n_arms) and ((t - n_arms) % n_users == 0):
        # We are at the end of the first subsequence corresponding to
        # initialization or classic. Therefore, we must correct the offsets.
        for user in users:
            if user.collided_in_subsequence:
                user.offset = random.randint(0, user.n_users - 1)

best_arms = np.sort(np.array(arm_means))[-n_users:]
regret = np.cumsum(n_best_arms.sum() - total_rewards)
plt.plot(range(t_horizon), regret, linewidth=2)
plt.legend("regret")
plt.show()
