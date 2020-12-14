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
    - [X] Implement SAR observer
        - Satellite pass simulation (use https://github.com/skyfielders?)
    - [X] Implement SAR analyzer
    - [X] Integrate multiple sources of analysis data in working simulation.
    - [X] Implement better method of reporting on and analyzing detection latency.
    - [ ] Implement analytics/visualization of detection latency and false positives changing over time.
    
    
    
    
* Final list:
 - [X] Make simulation support free roaming and local modes.
 - [ ] Implement remaining "easy" observer methods
    - [X] Fix queueing problem for SAR satellite
    - [X] Standoff aircraft
    - [ ] Unattended ground sensors (near base)
    - [ ] GEO Sigint satellites - 5% per hour per TEL when not in EMCON.
 - [ ] Implement TEL destruction logic
 - [ ] Implement missile defense.
 - [ ] Improving tracking logic.
 - [ ] Implement cued intelligence sources