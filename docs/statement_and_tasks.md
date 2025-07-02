# CS6620 Final Project: Problem Statement and Constituent Tasks
## Problem Statement
Healthcare providers often need a fast and reliable, yet easily comprehensible drug interaction checking system in order to analyze complete patient medication lists to prevent adverse drug reactions. Doing so allows them to optimize treatments, especially in cases where patients are taking multiple drugs at once (which is almost always the case). My brother's experience with epilepsy has also shown me the same. The current systems are often slow or require manual drug comparisons one at a time, risking hunan error or missing potential oversights that can lead to adverse drug reactions such as when medications make others less or more effective.

### *Overall Goals*
* Allowing for input of multiple medications
* Querying a database or drug API to check for interactions
* Returning interaction details that may or may not include severity level, type of interaction, potential alternative drugs, etc.
* System should be secure, fairly quick, and have a potential for scaling.
* NOTE: Goals will be open to adjustments depeding on what is technically feasible given the timeline.

## Constituent Tasks
### *POC User Stories*
1. Basic Two Drug Interaction
    * As a healthcare provider, I need to check if two specific medications would interact
2. Simple API Endpoint

### *MVP User Stories*

**for architecture diagrams, descriptions, and tradeoff options, please see `docs/architecture.pdf`*