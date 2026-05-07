# ITSD Tool



## Overview

IT Service Desk (ITSD) is a tool that allows managers and consultants to perform the steering of IT Service Desk services. This steering consists of managing, adding, updating, and removing various IT services such as MS Support, Outlook Support, etc. Furthermore, the tool includes functionalities for calculating FTE (Full Time Employee), which is a general measurement used for planning the resources of an IT support team. Additionally, there is a Forecast function, which can be used to provide predictions of possible changes caused by adjustments in specific parameters of the IT service (Work Hours, Volume, etc.). The final major function of the tool is related to Budget planning, where yearly budgets for various services can be added. The budget is separated per month, with calculations for monthly averages and yearly averages. All of these functions represent the core activities of the ITSD steering team.

The idea of this tool is to automate and improve the process of resource and budget management for IT services by switching from Excel spreadsheets to a fully functioning web application with a database.

## Description
### Add/Update Services
This functionality allows managers to add new IT services with all of their corresponding parameters needed for project management (Working Hours, Max Load, Flat FTE, Min FTE, etc.). After adding the IT service, it can be updated with new information if needed. Additionally, from this function a Budget record can also be created for a specific year chosen by the user, so that the budget planning can be initiated. Lastly, if a service is no longer needed, it can be removed, which will also trigger the removal of all records related to that service. Here, it must be considered whether these records should be kept as an archive or fully deleted.

### FTE calculation
This functionality allows managers to calculate the FTE (Full Time Employee), a unit of measurement used for workload planning. The functionality provides real-time data from the database, which is selected and displayed to show all related parameters used in the calculation of FTE. Additionally, there is a Forecast functionality (estimating future changes) using the same data, which can be manipulated in various ways to see how different parameters may affect the result.

### Budget calculation
This functionality allows managers to calculate the yearly and monthly budget for each IT service available in the database. The data is separated per year. All 12 months are available, as well as automatic calculations for the average per month and the average per year. All values are updated automatically whenever new input is entered. At the end, the data can be saved and stored in the database for further use. At any time, the data can be revisited and edited, which will also update the corresponding average calculations.




## Source Files

- **app.py** - Main file of the MVC model, acting as the Controller. Here, Python and Flask are used to control the entire process of synchronization and routing between the front end (API) and the backend (database).
- **/static** - Folder containing the styling of the interface, as well as images used to improve the user experience.
- **budget.html** - Contains the budget functions used for various calculations and operations within the budget module.
- **fte.html** - Contains the FTE calculation and Forecast functionality. It provides live data from the backend combined with the ability to manipulate the data for forecasting.
- **services.html** - Contains the functionalities related to adding, updating, and deleting IT services. The data of each service can be modified if updates are available or if changes are required. Additionally, this part of the application is responsible for creating Budget records, which are needed by budget.html.
- **index.html** - Main page of the application after logging into the system. It contains the three central functions of the tool.
- **layout.html** - Contains the layout of the app, along with additional structure and imported libraries.
- **login.html** - Login page for the app. It uses standard UX patterns for authentication and provides the possibility to register a new user account. This functionality can be further improved in the future, e.g., by integrating SSO instead of manual registration.
- **register.html** - Registration page for the app. A username and password must be entered to create an account. Standard security and integrity measures are followed to protect the app from cyberattacks.

## Libraries

Bootstrap - Main library used for the interface of the app. Here, different functionalities such as modal messages, confirmations, alerts, etc., are used. Additionally, most of the styling relies on Bootstrap’s capabilities.
Flask - Main framework for the app, following MVC principles. Various libraries were imported into the Flask application (e.g., password management, error handling, etc.).

## Conclusion:
With this tool, ITSD Tool, I created an optimization and improvement of the current process of steering the IT Service Desk team. This is a real company process issue that required optimization due to the manual procedures followed by the managers. By combining my IT knowledge gained from CS50 with my professional vision, I created an app that automates this process, improves data integrity, and makes the working experience easier for my colleagues. I do not consider the app to be in its final state, as there are many more optimizations that can be made and integrated in the future. This is just the beginning of one vision becoming reality and improving the quality of life for the people who will use this tool.

