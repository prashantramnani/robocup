import numpy as np
import pylab as pl

from pykalman.datasets import load_robot
from pykalman import KalmanFilter

n_timesteps = 51
print(n_timesteps)
n_dim_state = 2
print("nds",n_dim_state)

x = np.zeros(51)
y = np.linspace(0,50,51)
x=[[i] for i in x]
y=[[i] for i in y]

observations = np.concatenate((x,y),axis=1)

# Initialize the Kalman Filter
data = load_robot()
kf = KalmanFilter(
    np.eye(2), #data.transition_matrix (dim,dim)
    np.eye(2), #data.observation_matrix,(2,dim)
    np.eye(2), #data.initial_transition_covariance,(dim,dim)
    np.transpose(np.eye(2)), #data.initial_observation_covariance,[(0,val),(val,0)]
    observations, #data.transition_offsets,(500,dim)
    np.array([1,1]), #data.observation_offset,(2)
    np.ones(2), #data.initial_state_mean,(dim)
    np.eye(2), #data.initial_state_covariance,(dim,dim)
    random_state=0
)

# Estimate mean and covariance of hidden state distribution iteratively.  This
# is equivalent to
#
# (filter_state_means, filtered_state_covariance) = kf.filter(data)
filtered_state_means = np.zeros((n_timesteps, n_dim_state))
# print("fsm:",filtered_state_means,filtered_state_means.shape)
filtered_state_covariances = np.zeros((n_timesteps, n_dim_state, n_dim_state))
# print("fsc:",filtered_state_covariances,filtered_state_covariances.shape)



# print ("dto: ",data.transition_offsets[0])
# print ("fsm: ",filtered_state_means[0])
# print ("fsc: ",filtered_state_covariance[0])
# print ("dtm: ",data.transition_matrix)
# print ("om: ",data.observation_matrix)

TF = np.array([1.,1.])


for t in range(n_timesteps - 1):
    if t == 0:
        filtered_state_means[t] = [0,0]
        filtered_state_covariances[t] = np.eye(2)
    filtered_state_means[t + 1], filtered_state_covariances[t + 1] = (
        kf.filter_update(
            filtered_state_means[t],
            filtered_state_covariances[t],
            observations[t + 1],
            transition_offset=TF,
        )
    )

# draw estimates
pl.figure()

print filtered_state_means
lines_true = pl.plot(observations[:,0],observations[:,1], color='b')
lines_filt = pl.plot(filtered_state_means[:,0],filtered_state_means[:,1], color='r')
pl.legend((lines_true[0], lines_filt[0]), ('true', 'filtered'))
pl.show()