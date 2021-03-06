""" The module contains functions that allows to make training and testing from DYNAP-se samples
"""

import numpy as np
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

### ===========================================================================
def sklearn_fit(matrix, target):
    """Apply linear regression and find the coefficients to fit matrix in target
        
It uses the sklearn linear regression algorithm.

Parameters:
    matrix (2D array, float): Matrix that encodes spike
    target (array, float): Vector of target values

Returns:
    (tuple): tuple containing:

        - **regr** (*obj linear regression*): Object used for linear regression
        - **coefficients** (*list of float*): Contains coefficients of the regression
"""
        
    # Reshape matrix to get an array in format (time step, neurons) required by sklearn
    matrix = matrix.T
    target = target.T

    # Train the model using the training sets
    # The flow is the following:
        # input signal y --> (n, 1)
        # neuronFireRate X --> (1024, n) [should be transposed to (n, 1024)]
        # We should find a vector v such that <v, X> = y
    regr = linear_model.LinearRegression()
    regr.fit(matrix, target)
    coefficients = regr.coef_
    return regr, coefficients

### ===========================================================================
def sklearn_prevision(regr, matrix):
    """Make a target prevision using the previously found coefficients
        
It uses sklearn coefficients and prevision method

Parameters:
    regr (obj linear regression): Object used for linear regression
    matrix (2D array, float): Matrix that encodes spike

Returns:
    array, float : The performed prediction
"""
    
    # Transpose input matrix
    matrix = matrix.T
    prediction = regr.predict(matrix)
    return prediction
        
### ===========================================================================
def pseudo_inv_fit(matrix, target):
    """Apply linear regression and find the coefficients to fit matrix in target
        
It uses the pseudo inverse fitting algorithm

Parameters:
    matrix (2D array, float): Matrix that encodes spike
    target (array, float): Vector of target values

Returns:
    array, float : Coefficients of the regression
"""
    
    # ============ FEDERICO WAY ===============
    ## Reshape to get an array in format (n, 1) --> required for fitting
    #matrix = np.array(matrix)
    #target = np.array(target).reshape((-1, 1))
        
    ## y = X * b --> linear system where b is the vector we are searching (decoders)
    ## b = inv(X'X) X'y ---> b = pseudoinv(X'X) X'y
    #    # should be equivalent:
    #    # gamma = X*X'
    #    # upsilon = Xy
    #    # b = pseudoinv(gamma)*upsilon
    #gamma = np.dot(matrix, matrix.T)
    ## Apply regularization adding some Gaussian noise close to 1 in the diagonal
    ##gamma = gamma + np.eye(len(gamma)) * np.random.normal(loc = 1, scale = 0.15, size = len(gamma))
    #upsilon = np.dot(matrix, target)
    #ginv = np.linalg.pinv(gamma)

    ## Calculate coefficients
    #coefficients = np.dot(ginv,upsilon)

    # ============ NORMAL WAY ===============
    # Transpose to have a matrix with shape (time step, neurons)
    matrix = matrix.T

    # Calculate pseudo inverse
    pinv = np.linalg.pinv(matrix)

    # Retrieve coefficients
    coefficients = np.dot(pinv, target.T)

    return coefficients

### ===========================================================================
def pseudo_inv_prevision(coefficients, matrix):
    """Make a target prevision using the previously found coefficients
        
It uses pseudo inverse coefficients and prevision method

Parameters:
    coefficients (array, float): Coefficients that should be used for the prevision
    matrix (2D array, float): Matrix that encodes spike

Returns:
    array, float : The performed prediction
"""
        
    # Traspose matrix to have (time, neurons)
    prediction = np.dot(matrix.T, coefficients)
    return prediction

### ===========================================================================  
def prediction_plot(timeScale, prediction, target, ax = None):
    """Plot the prediction and the corrent output together
    
Parameters:
    timeScale (array, float): Time steps in which firing rate has been calculated
    target (array, float): Vector of target values
    prediction : numpy array of floats. Contains the performed prediction 
    ax (ax handle, optional): Plot graph on this handle

Returns:
    (tuple): tuple containing:

        - **figList** (*list of fig handles*): To modify properties of the figure
        - **axList** (*list of ax handles*): To modify properties of the plot
        - **handlesList** (*list of lines handles*): To create custom legends
"""
        
    fig = None

    # If no subplot is specified, create new plot
    if ax == None: 
        fig = plt.figure()
        ax = fig.add_subplot(111)

    handles = []

    handle = ax.plot(timeScale, target,  linestyle = 'None', marker = 'o')
    handles.append(handle)
    handle = ax.plot(timeScale, prediction, linestyle = 'None', marker = 'o')
    handles.append(handle)
    
    return fig, ax, handles
        
### ===========================================================================  
def prediction_performances(prediction, target, firingRateThreshold):
    """Print the mean square error and r2 score of the prediction

Parameters:
    target (array, float): Vector of target values
    prediction (array, float): The performed prediction
    firingThreshold (float): Threshold for determining neuron output
"""
    
    # Discriminate elements if above or below the chosen threshold
    prediction = prediction > firingRateThreshold
    target = target > firingRateThreshold

    # Take the difference between prediction and target
    # If there is a difference for at least an output neuron, the whole sample is wrong
    diff = np.any((prediction != target), axis = 1)

    # Count how much samples are wrong and how much are true
    wrongs = np.count_nonzero(diff)
    rights = len(diff) - wrongs

    return rights, wrongs

### ===========================================================================  
def av_fireRate_matrix_diff(M1, M2):
    """Calculate indicators that give hints about the difference between two matrices
    
The indicators are:\n
- nDiffNeuronAv: it tells in average how many neurons have a different firing rate
                    between the matrixes. It is expressed in percentage of the
                    average number of neurons that fire (in the two matrixes)
- diffFiringAv: it tells the average firing rate different between the matrixes.\
                    It is expressed in percentage of the average firing rate of the matrixes

Parameters:
    M1 (2D array, float): First matrix for the comparizon
    M2 (2D array, float): Second matrix for the comparizon
"""
    
    # Calculate the distance between matrixes (correspond to the number of differences in the experiment)
    M1 = np.array(M1)
    M2 = np.array(M2)
    diff = np.abs(M1 - M2)
    
    # Calculate the average (in time) of the number of neurons that fires in both matrix
    nNeuronM1 = np.mean((M1 != 0).sum(axis = 0))
    nNeuronM2 = np.mean((M2 != 0).sum(axis = 0))
    nNeuronAv = (nNeuronM1 + nNeuronM2) / 2
    
    # Calculate the average (in time) of the number of differences between the matrixes
    # Note that this result is expressed in percentage with respect to the average
    # number of neurons that fires
    nDiffNeuronAv = np.mean((diff != 0).sum(axis = 0)) / nNeuronAv * 100
    
    # Calculate the average (in time) firing rate in both matrixes -> for only the neurons that fire
    # Just do manually the average and delete the nan (neuron that does not fire)
    firingM1 = np.nanmean(np.true_divide(M1.sum(axis = 0), (M1 != 0).sum(axis = 0)))
    firingM2 = np.nanmean(np.true_divide(M2.sum(axis = 0), (M2 != 0).sum(axis = 0)))
    firingAv = (firingM1 + firingM2) / 2
    
    # Calculate the average (in time) of the firing rate differences between the matrixes
    # Note that this result is expressed in percentage with respect to the average
    # firing rate of both the matrixes
    diffFiringAv = np.nanmean(np.true_divide(diff.sum(axis = 0), (diff != 0).sum(axis = 0))) / firingAv * 100
    
    # Print at screen the results
    print("Firing rate matrix difference : ")
    print("Average different neuron : ", nDiffNeuronAv, "%")
    print("Average difference firing rate : ", diffFiringAv, "%")
    print()