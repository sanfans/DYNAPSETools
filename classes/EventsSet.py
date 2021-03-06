"""Contains a class that represent a set of DYNAP-se events
"""

import numpy as np
from matplotlib import pyplot as plt

class EventsSet:
    """A set of DYNAP-se events
    """

    def __init__(self, ts, chip_id, core_id, neuron_id):
        """Return a new EventsSet object

Parameters:
    ts (array, float): Times of events
    chip_id (array, int): Chip number of events
    core_id (array, int): Core number of events
    neuron_id (array, int): Neuron number of events

Note:
    The event set contains only *normal* events, not *special* ones.

    Events has the following structure:

    +------------+------------+-----------+-----------+-----------+ 
    | Vect       | Event 0    |  Event 1  | Event 2   | Event ... |
    +============+============+===========+===========+===========+ 
    | chip_id    | 0          | 1         | 3         | ...       | 
    +------------+------------+-----------+-----------+-----------+ 
    | core_id    | 0          | 3         | 1         | ...       |
    +------------+------------+-----------+-----------+-----------+ 
    | neuron_id  | 1          | 100       | 255       | ...       | 
    +------------+------------+-----------+-----------+-----------+
    | ts         | 150000     | 150064    | 150128    | ...       |
    +------------+------------+-----------+-----------+-----------+

    Accessing directly events from an .aedat is very simple, after having imported them::

        set = import_events("recording.aedat") # event set of the recording
        chip_id = set.chip_id
        core_id = set.core_id
        neuron_id = set.neuron_id
        ts = set.ts

    We can now access every event::

        >>> chip_id[0]
            0
        >>> core_id[0]
            0
        >>> neuron_id[1]
            100
        >>> ts[2]
            150128
"""

        self.ts = ts
        self.chip_id = chip_id
        self.core_id = core_id
        self.neuron_id = neuron_id

    def __getitem__(self, key):
        """Return a time filtered EventsSet object

Parameters:
    key (tuple, ints): a tuple containing an init and an end index

Note:
    This attribute is very useful when you want to isolate some events for which you know
    the indexes.

Example:
    - Isolate first 10 events::

        set = import_events("recording.aedat") # event set of the recording
        filteredSet = set[0:10]
"""
        init, end = key
        return EventsSet(self.ts[init:end], self.chip_id[init:end], self.core_id[init:end], self.neuron_id[init:end])

### ===========================================================================
    def filter_events(self, chip_id, core_id, neuron_id):
        """Return a EventsSet containing only the wanted events

Parameters:
    chip_id (int): id of the chip you want to take events from (for now is only possible to filter one chip events)
    core_id (list, int; int): id of the cores you want to take event from
    neuron_id (2D list, int; list, int; int): id of the neurons you want to take events from

Returns:
    obj EventsSet: A set containing the events resulting from the filtering

Note:
    Filter is specified selecting certain chip_id, core_id and neuron_id.
    It supports only one chip at a time (so chip_id must be a integer from 0 to 3), so you cannot take, for example,
    events from core 0 of chip 0 and core 1 of chip 1.
    
    After selecting the chip_id you have two alternatives: Or don't apply filters to the cores, by leaving core_id as None.
    In this way the events of all cores can be potentially taken, **if no neuron_id is specified**. The other alternative is to
    specify the cores you want to take events from, filtering the ones not specified by you. You can at this point define:

    1. a single core id, between 0 and 3.
    2. list of cores id, for example [0, 2].

    At this point you have two alternatives: Or don't apply a filter to the neurons inside a core, by neuron_id as None.
    In this way you will take all the events from the 256 neuron per core (only the one specified in the core filter, of course).
    The other alternative is to specify the neurons you want to take events from, filtering the ones that are not specified by you.
    If this is the case, you **must define something for all cores selected in the previous point**. You can define:

    1. a single neuron id, between 0 and 255
    2. a list of neurons id, for example [1, 5, 22, 128, ...]

    The types can be mixed, so you can take a single neuron from one core and a list from another, indipendently.

Examples:

    Initialize set importing all events::

        set = import_events("recording.aedat") # event set of the recording
        
    - Take events from chip 0, neuron from 0 to 99 of core 0 and neurons from 100 to 199 on core 1::

        filterCore0 = list(range(0, 100))
        filterCore1 = list(range(100, 199))
        neuronIdFilter = [filterCore0, filterCore1]
        filteredSet = set.filter_events(chip_id = 0,
                                        core_id = [0, 1],
                                        neuron_id = neuronIdFilter)
      
    - Take all events from chip 1::
            
        filteredSet = set.filter_events(chip_id = 1, core_id = None, neuron_id = None)

    - Take all events from core 0 and 1 of chip 2::

        filteredSet = set.filter_events(chip_id = 2, core_id = [0, 1], neuron_id = None)

    - Take only events from neuron 3 of core 0 and chip 3::

        filteredSet = set.filter_events(chip_id = 3, core_id = 0, neuron_id = 3)

    - Take events from chip 0, neuron 20 of core 0 and neuron 127 of core 1::

        filteredSet = set.filter_events(chip_id = 0, core_id = [0, 1], neuron_id = [20, 127])
"""
        
        #Check the core_id input to find events correlated with it*/
        filter_core_id = np.zeros(len(self.core_id), dtype = bool) # Initialization to all false
        try: # If 'for' not fails -> multiple cores
            for current_id in core_id: # Take events for all the cores
                filter_core_id = filter_core_id | (self.core_id == current_id) 
        except: # If 'for' fails -> single core
            filter_core_id = filter_core_id | (core_id == None)| (self.core_id == core_id) # Take events only for a certain core
        
        # Check the neuron_id input to find events correlated with it*/    
        filter_neuron_id = np.zeros(len(self.neuron_id), dtype = bool) # Initialization to all false
        try: # If 'for' not fails -> multiple lists (or just one)
            for core_index, neuron_list in enumerate(neuron_id):
                try: # If 'for' not fails -> multiple neurons
                    for current_id in neuron_list: # Take events only for a certain neuron and a certain core
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (self.neuron_id == current_id))
                except: # If 'for' fails -> single neuron
                    try: # If it not fails means that core_id is a list, so we have a list of single neurons
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (neuron_list == None))
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (self.neuron_id == neuron_list))
                    except: # If it fails means that core_id is a number, so we have a single list of neurons
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id) & (self.neuron_id == neuron_list))
        except:
            filter_neuron_id = filter_neuron_id | (neuron_id == None)| (self.neuron_id == neuron_id)
            
        # Combine all filters and apply them, getting only the events that has been selected*/    
        indx_neurons = (self.chip_id == chip_id) & filter_core_id & filter_neuron_id
        try:
            return EventsSet(self.ts[indx_neurons], self.chip_id[indx_neurons], self.core_id[indx_neurons], self.neuron_id[indx_neurons])
        except:
            errorString = "Error while filtering neuron events, no spikes found, check the constrains"
            raise NameError(errorString)

### ===========================================================================
    def isolate_events_sets(self, startTriggerNeuron, stopTriggerNeuron, maxNumber = None):
        """Returns a list of Event sets each one containing an experiment.

Parameters:
    startTriggerNeuron (tuple, int (chip id, core id, neuron id)): Neuron which events triggers the start of the experiment
    stopTriggerNeuron (tuple, int (chip id, core id, neuron id)). Neuron which events trigger the end of the experiment
    maxNumber (int): max number of experiments that can be extracted from the Set of events

Returns:
    list, obj EventsSet: a list of Event sets each one containing an experiment

Note:
    When dealing with Dynap-se output recordings, one of the main problems is "how get only events that are associated only with my input?"
    You can, of course, filter events manually using custom functions, but this is expensive in terms of time.
    An automatic solution, however, can be to use two Dynap-se neurons to trigger the start and the end of the events correlated to my input.

    The experiment would be constructed in this way:

    1. send a spike to a neuron that will represent my starting trigger
    2. send the experiment input spikes after small delay, negligible with respect to the delays involved in the input stream
    3. send a spike to a neuron that will represent my ending trigger, with a small delay, as for the input

    So each experiment is the repetition of these 3 passages. Make sure there is enough delay between the stop trigger event and the
    start of the new one. You should avoid overlapping of them, because this can create confusion while extracting events.
    The code is able to handle multiple spikes of start and trigger neurons for the same experiment, so don't much worry about that.

    This function should be applied to the output recording in order to filter all events but for the ones that are between
    the start and stop neurons. In this way you can automatically synchronize your analysis with the events generated only by your input.
    
    It is possible to specify also a maximum number of experiments that are extracted from the set using maxNumber parameter.

Examples:
    ::
        
        # Initialize set importing all events
        set = import_events("recording.aedat") # event set of the recording

    - startTriggerNeuron neuron 64 of core 2 of chip 0, stopTriggerNeuron is neuron 128 of core 2 of chip 0. Take all experiments (no maxNumber specified) included between these two neurons::
        
        startTriggerNeuron = (0, 2, 64)
        stopTriggerNeuron = (0, 2, 128)
        extractedEvents = set.isolate_events_sets(startTriggerNeuron = startTriggerNeuron,
                                                  stopTriggerNeuron = stopTriggerNeuron,
                                                  maxNumber = None)

    - startTriggerNeuron neuron 64 of core 2 of chip 0, stopTriggerNeuron neuron 128 of core 2 of chip 0. Take UP TO 5 experiments between these two neurons::

        startTriggerNeuron = (0, 2, 64)
        stopTriggerNeuron = (0, 2, 128)
        extractedEvents = set.isolate_events_sets(startTriggerNeuron = startTriggerNeuron,
                                                  stopTriggerNeuron = stopTriggerNeuron,
                                                  maxNumber = 5)
"""
        
        # If absolute index, convert to tuple containing (core, neuron id)
        #if not isinstance(startTriggerNeuron, collections.Iterable):
        #    startTriggerCore = (int) (startTriggerNeuron / 256)
        #    startTriggerNeuron = (startTriggerCore, startTriggerNeuron % (256 * startTriggerCore))
        #if not isinstance(stopTriggerNeuron, collections.Iterable):
        #    stopTriggerCore = (int) (stopTriggerNeuron / 256)
        #    stopTriggerNeuron = (stopTriggerCore, stopTriggerNeuron % (256 * stopTriggerCore))
        
        # Find the index of the start trigger neurons or stop trigger neurons
        startTriggerIndexes = np.where((self.chip_id == startTriggerNeuron[0]) &
                                       (self.core_id == startTriggerNeuron[1]) &
                                       (self.neuron_id == startTriggerNeuron[2]))[0]
        stopTriggerIndexes = np.where((self.chip_id == stopTriggerNeuron[0]) &
                                      (self.core_id == stopTriggerNeuron[1]) &
                                      (self.neuron_id == stopTriggerNeuron[2]))[0]

        # Setup experiment list
        experiments = []

        # Sweep over all requested experiments number
        startTrigger = 0
        stopTrigger = 0

        # Initialize the number of experiments to be taken
        counter = 0
        if maxNumber == None:
            limit = 0
        else:
            limit = maxNumber

        while ((maxNumber == None) | (counter < limit)):
            try:
                # Calculate the start and stop trigger of the current experiment
                startTrigger = startTriggerIndexes[startTriggerIndexes >= stopTrigger][0] # Start trigger should happen after the previous end trigger
                stopTrigger = stopTriggerIndexes[stopTriggerIndexes >= startTrigger][0] # End trigger should happen after start trigger

                # Filter the spikes information according to the previous range (the +1 is in order to take also the trigger spike)
                # Start and stop trigger are included!
                ts_event = self.ts[startTrigger:(stopTrigger+1)]
                neuron_id_event = self.neuron_id[startTrigger:(stopTrigger+1)]
                core_id_event = self.core_id[startTrigger:(stopTrigger+1)]
                chip_id_event = self.chip_id[startTrigger:(stopTrigger+1)]

                # Append experiment and increment counter
                experiments.append(EventsSet(ts_event, chip_id_event, core_id_event, neuron_id_event))
                counter = counter + 1
            except:
                break;

        # Check if there are experiments in the list
        if len(experiments) == 0:
            errorString = "Error while extracting experiments, cannot find any valid one: "
            errorString += "Check start and stop trigger neurons, or maxNumber value"
            raise NameError(errorString)
        else:
            print("Extracted {} experiments".format(len(experiments)))
            return experiments

### ===========================================================================
    def plot_events(self, ax = None):
        """Raster plot of events included in the current EventsSet

Parameters:
    ax (ax handle, optional): Plot graph on this handle, otherwise a new figure will be created

Returns:
    (tuple): tuple containing:
        
        - **fig** (*fig handles*): To modify properties of the figure
        - **ax** (*ax handles*): To modify properties of the plot
        - **handles** (*lines handles*): To create custom legends

Note:
    Colors has been chosen to be clearly visible and to match the DYNAP-se core color enconding::

        - core 0: green
        - core 1: magenta
        - core 2: red
        - core 3: yellow

    With this classification there there is no distinguish between different chips events. It is much better
    to filter them and display them separately.

    The input ax value can be used to make it plot over a pre-created figure. Fig, ax and handles can be used instead
    by the user to specify in detail the properties of the graph (see Example for how to do it)

Examples:
    ::

        # Initialize set importing all events
        set = import_events("recording.aedat") # event set of the recording
        figList, ax, handles = set.plot_events() # plot events
        ax.set_title("Raster plot Recording")
        ax.set_xlabel('time [us]')
        ax.set_ylabel('Neuron id')
"""

        fig = None

        # If no subplot is specified, create new plot
        if ax == None: 
            fig = plt.figure()
            ax = fig.add_subplot(111)

        handles = []
        # Plot different cores with different colors
        for core in range(4):
            indx_core = np.where((self.core_id == core))[0] # Search for events of a core
            
            if core == 0:
                color = 'g'
            elif core == 1:
                color = 'm'
            elif core == 2:
                color = 'r'
            else:
                color = 'y'
                
            handle, = ax.plot(self.ts[indx_core], self.neuron_id[indx_core] + 256 * core, linestyle = 'None', marker = 'o', color = color)
            handles.append(handle)

        return fig, ax, handles

### ===========================================================================
    def calculate_firing_rate_matrix(self, totNeurons, numBins = 10, timeBin = None):
        """Derive a firing rate matrix starting from the current EventSet
        
Parameters:
    totNeurons (int): Maximum number of neurons for which firing rate is calculated (from id = 0 to totNeuron number)
    numBins (int): Default parameter. Number of intervals in which firing rate must be evaluated
    tBin (int, [s], optional): Amplitude of each interval in which firing rate must be evaluated

Returns:
    (tuple): tuple containing:

        - **timeSteps** (*array, float*): Time steps in which firing rate has been calculated
        - **neuronsFireRate** (*2D array, float*): Contain firing rate for every neuron and for every time step

Note:
    To evaluate the firing rate the average of the spikes is made over a certain time step. The rate value is then associated
    to the first time in the time bin, as here below::

        timeSteps -> [t0 t0+tBin t0+2tBin ... tn-tBin]
    
    where tBin is the temporal step in which firing rate is evaluated (tBin = (tn - t0) / numBins)) or directly the specified tBin

    The firing rate is calculated for every specified neuron, obtaining the following matrix (number are expressed in Hz):

    +------------+--------------+----------------+---------------+----------------+
    | neuron id  | fr at t0     | fr at t0+tBin  | ...           | fr at t0+ntBin |
    +============+==============+================+===============+================+
    | neuron 0   | 5            | 0              | ...           | 0              |
    +------------+--------------+----------------+---------------+----------------+
    | neuron 1   | 0            | 10             | ...           | 10             |
    +------------+--------------+----------------+---------------+----------------+
    | ...        | 2            | 2              | ...           | 2              |
    +------------+--------------+----------------+---------------+----------------+
    | neuron n   | 20           | 10             | ...           | 10             |
    +------------+--------------+----------------+---------------+----------------+

Examples:
    ::

        # Initialize set importing all events
        set = import_events("recording.aedat") # event set of the recording

        # obtain firing rate from number of bins
        timeSteps, neuronsFireRate = set.calculate_firing_rate_matrix(totNeurons = 1024,
                                                                      numBins = 100)
        
        # obtain firing rate from bin size
        timeSteps, neuronsFireRate = set.calculate_firing_rate_matrix(totNeurons = 1024,
                                                                      timeBin = 0.02)
"""
        
        # Initialize vectors
        timeSteps = []
        #neuronSpikes = [[] for count in np.arange(totNeurons)]
        neuronsFireRate = [[] for count in np.arange(totNeurons)]
        absoluteNeurons = (self.chip_id * 1024) + (self.core_id * 256) + self.neuron_id

        # Calculate time bins
        if timeBin != None: # If time bin is fixed and the number of bins are variable
            binSize = timeBin * 1000000 # Transform in [us]
            time = self.ts[0]
            timeBins = [time]
            while time <= self.ts[-1]:
                time += binSize
                timeBins.append(time)
        else: # If time bin is variable and the number of bins are fixed
            timeBins, binSize = np.linspace(self.ts[0], self.ts[-1], numBins + 1, retstep = True)
        timeBins = [(timeBins[i], timeBins[i + 1]) for i in range(len(timeBins) - 1)]
        
        # Sweep over the time bins and calculate spikes and firing rate
        for timeBin in timeBins:
            timeSteps.append(timeBin[0])
            # Initialize to 0 the firing rate of all neurons
            for pos in np.arange(totNeurons): 
                #neuronSpikes[pos].append(0)
                neuronsFireRate[pos].append(0)
            # Find the spikes in the time Bin
            spanInterval = np.where((self.ts >= timeBin[0]) & (self.ts < timeBin[1]))[0]
            # Span the spikes and increment the spike counter in the neuron list
            for pos in spanInterval:
                #neuronSpikes[absoluteNeurons[pos]][-1] += 1
                try:
                    neuronsFireRate[absoluteNeurons[pos]][-1] += 1
                except:
                    pass
            for pos in range(totNeurons): # Do the average in all neurons
                #neuronFireRate[pos][-1] = neuronSpikes[pos][-1] / (binSize / 1e6)
                neuronsFireRate[pos][-1] = neuronsFireRate[pos][-1] / (binSize / 1e6)

        return np.array(timeSteps), np.array(neuronsFireRate)

### ===========================================================================
    def normalize(self):
        """Normalize the time of the current EventSet

Returns:
    obj EventsSet: A new normalized EventSet

Note:
    The time of the first event is set to 0. The subsequent are changed accordingly
"""
        return EventsSet(self.ts - self.ts[0], self.chip_id, self.core_id, self.neuron_id)