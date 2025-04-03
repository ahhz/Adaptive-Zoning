# Copyright (c) 2025 Alex Hagen-Zanker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Estimate beta
import numpy as np
import scipy.spatial 
#  points must be n x 2 numpy array
# calculates straight line distances between points

def distance_matrix_from_points(points):
    return scipy.spatial.distance.cdist(points, points)
 
# all inputs, except beta, must be numpy arrays
# solves the doubly constrained spatial interation model Tij = ai*bj*Oi*Dj*exp(-beta*dij)

def doubly_constrained(orig, dest, distance, beta, verbose = False):
    
    m,n = distance.shape
    assert(n > 0 and m > 0 and (m,) == orig.shape and (n,) == dest.shape)
    
    prior = np.transpose(orig) * dest * np.exp(-beta * distance)
    
    a = np.ones(m)
    b = np.ones(n)
    
    max_iteration = 100
    precision = 1e-6
    
    for i in range(max_iteration):
        a = orig / np.matmul(prior,b) 
        b_new = dest / np.matmul(np.transpose(a),prior)
        converged = np.all((b_new-b)**2 < precision)
        b = b_new
        if converged: 
            if verbose: print("Doubly constrained: Converged after ", i, " iterations")
            break
    
    trips = np.transpose(a) * b * prior;
    average_distance = np.sum(trips * distance) / np.sum(trips)
    return trips, average_distance, a, b   


# find the value for beta that reproduces the desired average distance, using bisection search
def calibrate_doubly_constrained(orig, dest, distance, target_average_distance, beta_min = 0, beta_max = 1, verbose = False):
   # high distance is associated with low beta
    average_distance_max = doubly_constrained(orig, dest, distance, beta_min, verbose = verbose)[1]
    average_distance_min = doubly_constrained(orig, dest, distance, beta_max, verbose = verbose)[1]
    
    if average_distance_max < target_average_distance:
        if verbose: print("calibrate_doubly_constrained: lower_bound is too high")
        return None
   
    if average_distance_min > target_average_distance:
       if verbose: print("calibrate_doubly_constrained: upper_bound is too low")
       return None
   
    while (beta_max - beta_min) > 1e-6:
       beta = (beta_min + beta_max) / 2
       average_distance = doubly_constrained(orig, dest, distance, beta, verbose = verbose)[1]
       if average_distance < target_average_distance:
           beta_max = beta
       else: 
           beta_min = beta

    return beta
