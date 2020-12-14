# config.py
Stores all parameters used by the model, including quantitative assumptions about TELs, US intelligence capabilities and nuclear arsenal, and China itself.

Configuration is stored in a series of Python classes that support overriding, so that the default config can be modified to create specialized configurations to represent different Chinese strategies under low, high, and medium alert levels.

# simulation.py
Contains the Simulation object which acts as a container for all other objects, and performs basic functions of running the simulation, including:
* Keeping track of the current time. Time in the simulation begins at noon on January 20th, 2021, and progresses in steps of one minute. Real times are used rather than offsets from an arbitrary "t=0" so that sunrise and sunset times can be simulated realistically.
* Running the simulation's event loop.

The simulation supports two main modes of operation:
* In Base Local mode, each TEL is considered to stay within a radius of its home base, returning after each trip. In this mode, TELs are linked together based on base affiliation, so e.g. TELs associated with the same base are assumed to experience the same weather.
* In Free Roaming mode, each TEL is assumed to wander throughout all of China independently, increasing the amount of sensor data that must be processed in order to find all of the TELs.

# enums.py
Contains low level data types (enumerations) used throughout the simulation, representing concepts such as the different states a TEL can be in, the different detection methods available to the US, and so on.

# location.py
Contains a Location class, representing a (lat, lon) coordinate pair. The main use of the Location object in this simulation is to allow calculating sunrise and sunset times for a given TEL base (determining whether nearby TELs are visible to EO satellites). This calculation takes into account both geographical position and the time of year.

# tel.py
Contains the TEL class, which represents either a TEL, or a Chinese decoy which is designed to look and behave similarly to a TEL. Each TEL independently transitions through a configured set of states based on the alert level (e.g. staying in base for 16 hours, then roaming for 8 hours). In addition, while in Free Roaming mode each TEL independently simulates weather conditions.

The TEL class also contains methods for reporting how far the TEL has roamed since it was last observed, and how many square km must be destroyed in order to cover all of the areas it could have roamed to in this time.

# tel_base.py
Contains the TELBase class, which holds a collection of TELs based at the same location. In Base Local mode, it also simulates local weather.

This module also contains functions for loading the set of TELs from an external data file.

# intelligence_types.py
Contains data types used to represent different stages of US collection and processing of intelligence data.

TLO: A TEL-Like-Object. Represents an object which the US may (rightly or wrongly) believe is a TEL. Every TEL and decoy has a corresponding TLO, and there are also TLOs to represent heavy trucks which could be mistaken for TELs. A single TLO object can represent multiple entities in the simulation, so it is possible to represent ~1 million trucks by a single object, allowing them to be simulated efficiently.

Observation: A piece of intelligence (processed or unprocessed) which the US has collected. It can correspond to a TLO, but it can also represent e.g. a satellite imagery tile that may not contain a TEL or TLO. Observations are marked with what detection modality created the observation (EO satellite, ground sensor, etc.), as well as when the observation occurred.

File: A File represents the information the US has collected about a given TEL. The US maintains one File for every TEL, and assigns Observations to a file when it believes them to correspond to it. When it comes time to assess the potential for a nuclear strike, it is the Observations in the Files which are used to do so.

# intelligience.py
Contains an Intelligence class, representing the efforts of the US intelligence apparatus to find and track TELs. It consists of a pipeline of operations:

1. A series of Observer classes (corresponding to different detection modalities) generate raw observations.
2. Corresponding Analyzer classes process these observations, attempting to determine which correspond to TELs.
3. A Tracker class takes the observations output from the Analyzers, and attempts to pair them to TEL files.
4. Finally, an assess() function is called to judge the odds of a successful first strike based on the data in the TEL files.

# observer.py
Contains several observer classes, all implementing an abstract Observer interface. Each Observer looks at the set of TLOs, and determines which it is able to observe at the current time, based on factors like cloud cover, daylight, TEL state, SAR satellite passes, and so forth. It then adds (a large amount of) observation objects representing raw sensor data which does not correspond to a TLO or TEL.

Contains implementations for EO and SAR satellites, offshore aircraft equipped with SAR sensors, signals intelligence with a low chance to detect TELs not practicing emissions control, and ground sensors with a good likelihood of detecting TELs entering or leaving the base.

# analyzer.py
Contains implementations of an abstract Analyzer interface. An Analyzer takes a series of observations as input each time step, and then outputs processed observations once it has finished processing them. The operations which are output are only the ones which are believed (by the possibly fallible analysis process) to correspond to real TELs. In reality, some of them may be non-TEL TLOs, such as trucks or decoys.

The ImageryAnalyzer models an AI-assisted image recognition process. It is assumed that large quantities of image data are processed first by an ML algorithm with a given false positive and false negative rate, and then by human analysts. Only a certain quantity of human analysts are available, so how quickly they are able to process a batch of data will depend crucially on how many non-TEL objects can be filtered out by the AI system.

# tracker.py
Contains implementation of the Tracker interface. Currently, only a "perfect" tracker, which always assigns TEL observations to the correct File, is implemented.

# assessor.py
Contains the implementation of the assess() method. This is called at each timestep to determine whether a first strike is possible. It works by first collecting the area around each TEL which must be destroyed, which varies based on how precisely the TEL's location is known. This area is calculated several times, based on the flight time delay of different US nuclear assets.

To complete the assessment, missiles in the US nuclear arsenal are matched up against TELs, starting with those whose location is most precisely known (and are thus easiest to destroy). Once enough missiles have been committed to a given TEL to guarantee destruction, it proceeds to the next. Ultimately, either an assignment which destroys all TELs is found, or there is some remaining amount of TELs with the ability to fire back at the US. This number is passed through a formula to determine the probability that at least one warhead gets through US missile defenses.

# renderer.py
Contains the Renderer class, which is responsible for generating charts and graphs based on the state of the simulation.