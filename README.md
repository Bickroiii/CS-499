# Grazioso Salvare Rescue Dog Dashboard

This repository contains my updated Grazioso Salvare Rescue Dog Dashboard for the CS 499 Computer Science Capstone.

The original project was created in CS 340 and was enhanced throughout CS 499 in three areas: software design and engineering, algorithms and data structures, and databases.

## Project Enhancements

### Software Design and Engineering

The project was improved by:

* Removing hardcoded database credentials
* Using environment variables for configuration
* Improving CRUD validation and error handling
* Preventing unsafe update and delete operations
* Replacing fragile column index references with named fields

### Algorithms and Data Structures

The project was enhanced by:

* Adding a rescue candidate scoring system
* Using dictionaries to store rescue requirements
* Using a heap to maintain the top rescue candidates
* Improving candidate selection to approximately O(N log K)
* Adding short term caching for repeated ranking requests

### Databases

The database portion was improved by:

* Adding MongoDB aggregation pipelines
* Adding compound indexes for common queries
* Adding audit logging for database operations
* Improving authenticated database access
* Moving some data processing from pandas into MongoDB

## Technologies Used

* Python
* MongoDB
* PyMongo
* Dash
* pandas
* Plotly
* Dash Leaflet
* JupyterLab
* GitHub Pages

## Purpose

The purpose of this project is to demonstrate how an existing application can be reviewed, improved, and expanded using software engineering, algorithmic, database, and security practices.

The final version of the dashboard is more secure, maintainable, efficient, and useful for identifying and reviewing potential rescue dog candidates.
