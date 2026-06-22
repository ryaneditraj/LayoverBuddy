# LayoverBuddy

This is a projct that i have made to make layovers easier and better


Mostly the flight site only show the price of the flight and the timing of the flight. I have built something that helps you compare with actual layover cities.

For example, if a person wants to go from New York to Chennai, there can be many different layovers as stated below. 

* Singapore
* Istanbul
* Dubai
* Doha

Some of these places can be better as compared to the other layovers, so I have built it to rank them.

---

# What it does

Right now, the project can do all of this:

* It can search routes
* Show layover cities
* Rank layovers
* Show airport information
* Give recommendations
* Show attraction information
* Show some basic statistics

---

# Route Search

User enters:

From City

To City

Example:

From:
Chennai

To:
New York

The system checks the route data and then it finds if there are any possible layovers, and if so, it gives some suggestions.

---

# Layover Suggestions

Example result:

* Singapore
* Istanbul
* Dubai
* Doha

---

# Ranking System

Layovers are sorted by score.

Higher score means better layover.

The ranking is based on a few different things.

---

# Airport Information

Every airport has some information stored.

Things included:

* Airport score
* Time needed to reach city
* Recommended layover hours
* Notes

Example:

Singapore

Airport Score:
98

Time To City:
30 mins

Best Layover:
8 hours

Note:
One of the best airports in the world.

---

# Recommendation System

The app gives simple recommendations.

Possible results:

* Excellent
* Very Good
* Good
* Average
* Not Recommended

---

# Statistics

Simple statistics page.

Shows things like:

* Number of airports
* Best airport
* Highest score

---

# Attraction Data

Some cities have attractions stored.

Example:

Singapore

* Marina Bay Sands
* Gardens by the Bay
* Merlion
* Chinatown
* Sentosa

---

# Project Structure

layoverbuddy/

app.py

layovers.py

airport_info.py

recommendations.py

attractions.py

routes.json

scores.json

airport_info.json

attractions.json

templates/

index.html

results.html

requirements.txt

---

# Tech Used

Backend:

* Python
* Flask

Frontend:

* HTML
* CSS

Storage:

* JSON files

No database yet.

---

# Setup

Install requirements:

pip install -r requirements.txt

Run project:

python app.py

Open browser:

http://127.0.0.1:5001

---

# Data Files

routes.json

Stores route data.

Example:

New York

Singapore

Istanbul

Dubai

Doha

---

scores.json

Stores layover scores.

Example:

Singapore = 95

Istanbul = 92

Dubai = 85

---

airport_info.json

Stores airport information.

Example:

Singapore

Airport Score = 98

City Time = 30

Best Hours = 8

---

attractions.json

Stores attraction lists.

Example:

Singapore

Marina Bay Sands

Gardens by the Bay

Merlion

---

# Scoring

Current score uses:

* Layover score
* Airport score
* City access time
* Layover duration

Example:

Layover Score = 95

Airport Score = 98

City Bonus = 15

Duration Bonus = 15

Final Score = 223

---

# Example

Input:

Chennai

New York

Output:

1. Singapore

Score = 223

Excellent

2. Istanbul

Score = 207

Very Good

3. Dubai

Score = 195

Very Good

4. Doha

Score = 184

Good

---

# Things I might add later on

Still not finished.

Need to add:

* Real flight APIs
* Real route data
* Visa information
* Transit visa checking
* Maps
* Accounts
* Saved trips
* Mobile support
* Flight comparison system

* Route comparison
* Maps
* Better airport explorer
* Better search

 Real flight APIs
* Real airport data
* Better recommendations

---

# Final Goal

User enters:

Chennai → New York

The system should show:

* Best layovers
* Airport ratings
* Attractions
* Time to city
* Recommendations
* Travel information

so people can choose a better layover instead of only choosing the cheapest flight.
