This project is the result of a coding challenge for a Python programmer position at Satellogic (https://satellogic.com) in 2015.

The task was to build a satellite fleet simulation and task scheduling system. Although there was no fixed deadline, I initially intended to spend only a few hours on it. However, it ended up taking around 12 hours, as I spent more time than expected refreshing certain concepts and improving the task assignment algorithm to find an optimal solution.

The interview and selection process were conducted entirely in Spanish, so the accompanying LEEME.txt file—containing design decisions, assumptions, and usage instructions—is written in Spanish. All code and comments, however, are in English.


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
  * Support a variable number of satellites                                              - Done
  * Tasks support the HOUR attribute, defining its execution time                          - Done
  * Distribution of tasks need to support variable failure probability for each satellite  - Done
  * Create a web interface to upload tasks                                                 - No, time constrained
  * Visualization of the historical registry                                               - No, time constrained
  * Justify all technical decisions and design choices                                     - Done
