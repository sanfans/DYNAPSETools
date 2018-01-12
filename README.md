# DYNAPSETools
The repository contains a set of tools that are useful to work with [DYNAP-se board](https://inilabs.com/products/dynap/).
It contains:
  * **DynapseNetGenerator** : permit to create a .txt file with encodes connections that can be programmed using [netparser](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.crkj98n9ian3) module.
  * **DynapseOutDecoder** : permit to retrieve from DYNAP-se recordings (.aedat files) spikes and plot them
  * **DynapseSpikesFitter** : permit to make training and testing starting from firing rate matrix of recordings
  * **DynapseSpikesGenerator** : permit to create a .txt file which encodes inputs that must be sent to DYNAP-se, using [FPGASpikeGen](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.3prdeugulxol) module.
### How to import
* Clone the repository with git in your python work folder
* Place the script that should use this folder in the same folder of the library

To import a module write:
```python
import DYNAPSETools.DynapseNetGenerator as netgen
import DYNAPSETools.DynapseOutDecoder as decoder
import DYNAPSETools.DynapseSpikesFitter as fitter
import DYNAPSETools.DynapseSpikesGenerator as spikegen
```
To use functions contained in the modules write
```python
netgen.functionToCall(...)
decoder.functionToCall(...)
fitter.functionToCall(...)
spikegen.functionToCall(...)
```

### SpikesGenerator
#### Description
DYNAP-se contains an useful module called FPGASpikeGenerator. This module allows the user to send customized (in address and interspike interval) spike patterns in specific location inside DYNAP-se.

A very simple way to understand the behavior of the Spike Generator is thinking about it as a VIRTUAL external chip outside DYNAP-se.
His main advanatage, with respect to the physical ones, is the flexibility. Events can be completely customized: you can select which neurons will spike and the interspike interval between spikes.

Virtual chip can be "connected" to the physical ones and stimulated whenever you want, making simpler the creation of customize tests for neural structure in DYNAP-se.

His main drawback is the connectivity limitation. Unfortunately only one physical chip can be connected, at the same time, to the virtual one, although this is enough to run complex test patterns.
For instance making a connection between one neuron in the virtual chip and Chip 0 will make impossible any other connection with the other 3 Chips.
Selection of the destination chip is done directly on the module interface.

Customized spiking patterns must be specified preparing a .txt file, containing two parameters:
 * **Source Neuron Address :**  number resulting by the combination of parameters `Neuron Address`, `Virtual source chip` and `Core Dest`. The first two are represent can be seen as neuron address and neuron core (yes, core, not chip) of the virtual chip. The third one, instead, is used for event routing. It specify, in fact, on which cores of the destination chip the spike will be trasmitted. For more informations visit [DYNAP-se user guide](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.3prdeugulxol)
 * **Interspike Interval** : number that represent the time between the current event and the previous one specified in the file, expressed in ISI base multiple (the first event delay can be considered as an initial delay). For more information visit [DYNAP-se user guide](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.3prdeugulxol)

In the following image is summarized the main characteristics of the Spike Generator. As said before, can be considered as a virtual chip (U4) made with Virtual Neurons. The txt file specify the characteristics of the generated events: address of the source neuron, interspike interval and core destinations. Note that in this case U2 has been chosen as destination chip.


<img src="./docs/images/spikeGen.jpg" width="500px"  />

An example of .txt file is the following one:

> ISIBase = 90 corresponding to 1 us time step
```
79, 20000
79, 20000
79, 20000
79, 20000
79, 10000
79, 10000
142, 20000
142, 20000
```
In this example address 79 is:
* `Neuron Address` 1
* `Virtual source chip` 0
* `Core dest` 15 (hot-encoded 1111, meaning to all cores)

While address 143 is:
* `Neuron Address` 2
* `Virtual source chip` 0
* `Core dest` 14 (hot-encoded 1110, meaning to cores 1, 2 and 3)

This file will generate 4 events with 20 ms of interspike interval (corresponding to 50Hz) on `Neuron 1`, then 2 events with 10 ms delay between them, finally 2 events on `Neuron 2` with 20 ms delay

It is evident that generating this file manually is not easy. Here is where class SpikesGenerator come to help. Inside there are functions that permit the user to create in many ways desired event patterns.
#### Functionalities
* Create events from lists containing informations about the neurons and absolute times
* Create constant frequency events as well as linear frequency modulation
* Encode a certain signal in spikes with two different encoding types:
  * Slope encoding: firing frequency depend on the ratio between the current slope of the signal and the maximum one
  * Threshold encoding: every time the signal step up or step down of an amount bigger than a threshold, a spike is generated. Maximum and minimum firing frequency depend on threshold amplitude
* Plot generated spike pattern. If they come from an encoded signal, it can be plotted too
* Write output .txt file containing coded events
* Possibility to import events from a .txt file, plot them and add new patters
* Possibility to stack as many patterns as needed just calling the apposite functions
#### Limitations

### DynapseNetGenerator
DYNAP-se contains an useful module called NetParser. This module simplify the way in which connections can be programmed on DYNAP-se board. For more informations about the module, visit [DYNAP-se user guide](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.crkj98n9ian3)