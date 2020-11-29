* Milestone 1: Rich TEL simulation
    - [X] Rewrite core simulation loop:
        - Real datetimes rather than integer second offsets.
        - Actual running of loop handled in a run() method rather than the ipynb notebook.
        - Automatically scheduled rendering.
    - [X] Create TEL state machine.
        - Support list of states, with transitions happening hourly based on a probability table.
        - Support different probability tables based on time of day and alert level.
        - Support configuring probability tables in a file (maybe)
        - Integrate a few TELs manually into the simulation for testing.
    - [X] Configuration of TELs.
        - Support loading missile base coordinates, with accompanying TEL info.
        - Add TELs to simulation from configuration.
    - [ ] Visualization of TELs.
        - Plot status of TELs by missile base on Folium map.

* Milestone 2: Simulated detection of TELs.
    - [X] Implement sunlight tracking for TEL bases.
    - [X] Implement basic skeleton of US intelligence tracking logic.
    - [X] Implement EO observer
    - [X] Implement EO analyzer
    - [ ] Implement SAR observer
        - Satellite pass simulation (use https://github.com/skyfielders?)
    - [X] Implement SAR analyzer
    - [X] Integrate multiple sources of analysis data in working simulation.
    - [ ] Implement better method of reporting on and analyzing detection latency.