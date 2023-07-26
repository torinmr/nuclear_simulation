# US-China Nuclear Confrontation Simulation

This is an event-based simulation of a hypothetical nuclear conflict between the
United States and China. The purpose of the simulation is to model how advancements
in AI, specifically large scale visual recognition using neural networks, might
affect the nuclear balance of power.

This simulation was programmed by Torin Rudeen, based on data and models provided by
Ben Chang, as part of Ben Chang's doctoral dissertation at MIT. You can read the
dissertation paper based on this simulation [here](Dissertation.pdf) (pages 70-125).

## Motivation

To give some brief context, China's nuclear deterrence strategy is based around having
a large number of mobile missile launchers, known
as [TELs](https://en.wikipedia.org/wiki/Transporter_erector_launcher), which are easy to
move around the country and hide. Thus, anyone who wished to launch a nuclear first
strike against China would be dissuaded, because it would not be feasible to
accurately track the location of every single TEL which could possible launch a
counterattack.

This simulation attempts to see whether this calculus could be changed by the
deployment of large-scale image recognition, which may make it possible to find TELs
in close to real time by analyzing satellite imagery and other data.

## Technical Details

The simulation is coded in Python, using iPython and Pip to make it easy to
reproduce and experiment with the results.

The simulation uses an event-based approach, where each event can trigger further
events to happen at a future timestamp. For example, when a missile is launched, the
simulation calculates how long it will take to arrive at its target, and enqueues a
future event for the missile's impact. It also calculates how long the launcher will
need to reload, and enqueues a future event for when the launcher will be able to
fire again.

There are several versions of the simulation in different subdirectories. A good entry
point for exploring each one is `lib/simulation.py`, which holds the core simulation loop
and initializes all of the other entities.
