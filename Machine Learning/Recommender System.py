import numpy as np
import scipy.optimize as op

def recommend_movies(user_id, n):
    return titles[np.argsort(predict[:,user_id], 0)[::-1][:n]]

def parameterize(X, theta):
    return np.hstack((X.flatten(), theta.flatten()))

def unparameterize(param, n_movies, n_users, n_feat):
    X     = np.matrix(param[:n_movies*n_feat].reshape(n_movies, n_feat))
    theta = np.matrix(param[n_movies*n_feat:].reshape(n_users,  n_feat))
    return X, theta

def normalize(y): # only take the mean of rated movies
    mu   = np.apply_along_axis(lambda x: np.mean(x[x > 0]), 1, y)
    norm = np.apply_along_axis(lambda x: x-mu, 0, y)
    return mu, norm

def compute_cost(theta, X, y, r, reg):
    X, theta = unparameterize(theta, n_movies, n_users, n_feat)
    h = np.multiply(r, X*theta.T-y)
    J = np.sum(np.sum(np.square(h)/2)) + reg/2*np.sum(np.sum(np.square(theta))) + reg/2*np.sum(np.sum(np.square(X)))
    grad = parameterize(h*theta + reg*X, h.T*X + reg*theta)
    return J, grad

titles = np.array(open("data/recommender/movies.txt").read().split("\n"))
y = np.matrix(np.genfromtxt("data/recommender/y.csv", delimiter=","))
r = np.matrix(y > 0)

reg      = 10
n_feat   = 10
n_movies = y.shape[0]
n_users  = y.shape[1]
X        = np.matrix(np.random.randn(n_movies, n_feat))
theta    = np.matrix(np.random.randn(n_users,  n_feat))
mu, norm = normalize(y)
result   = op.minimize(
            fun     = compute_cost,
            x0      = parameterize(X, theta),
            args    = (X, norm, r, reg),
            method  = 'TNC',
            jac     = True,
            options = {'maxiter': 100, 'disp': 5})
X, theta = unparameterize(result.x, n_movies, n_users, n_feat)
predict  = np.apply_along_axis(lambda x: x+mu, 0, X*theta.T)
print("Top 10 Movies for First User:\n- {}".format("\n- ".join(recommend_movies(0, 10).flatten())))

''' Output
Top 10 Movies for First User:
- Star Wars (1977)
- Return of the Jedi (1983)
- Empire Strikes Back, The (1980)
- Princess Bride, The (1987)
- Wrong Trousers, The (1993)
- Lawrence of Arabia (1962)
- Secrets & Lies (1996)
- L.A. Confidential (1997)
- Close Shave, A (1995)
- Casablanca (1942)
'''
