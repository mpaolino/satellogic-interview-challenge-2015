This is the result of a coding challenge as part of a selection process for a Python programmer role in 2015 at Satellogic (https://satellogic.com).

The problem was to create a satellite fleet simulation and task scheduling system. There was no deadline but I didn't want to spend too much time on it but
it ended taking me round 12 hours because I spend much more time than I expected by refreshing some concepts and improving the task assigment algorithm
to find an optimal solution.
The interview and process was all done in Spanish so the provided LEEME.txt which justifies the design decisions, assumptions and instructions
how to use it are all written in that language. All code and comments are in English.


Main objective
--------------
  * Create a system that simulates a ground station, satellite fleet and task assignment to maximize payoffs - Done

Definitions and constrains
--------------------------
  * Satellites are given scheduled tasks by the groundstation
  * Satellites have all the same resources available to them
  * There is only one groundbased station that schedules and assigns tasks to satellites
  * Tasks have a name, a payoff represented as a float and a list of resources they use
  * Satellites and groundstation need to be implemented using independent OS processes

Bonus points
------------
  * Historical registry of tasks and results                                               - Done
  * Support for variable number of satellites                                              - Done
  * Tasks support the HOUR attribute, defining its execution time                          - Done
  * Distribution of tasks need to support variable failure probability for each satellite  - Done
  * Create a web interface to upload tasks                                                 - No, time constrained
  * Visualization of the historical registry                                               - No, time constrained
  * Justify all technical decisions and design choices                                     - Done
