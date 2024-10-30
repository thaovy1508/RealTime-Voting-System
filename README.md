# Real Time Election Voting System
This repository is part of our group project for DS5110. We have chosen to develop a scalable, real-time voting system using big data technologies. We'll incorporate technologies like **Docker, Kafka, PostgreSQL, Python, Apache Spark, and Streamlit** to build a robust, scalable, live-updating voting platform. The system uses Docker Compose to quickly set up the needed services in Docker containers.

## System Architecture
![System_Architecture](images/system_architecture.png)
- The system processes votes in real-time using **Apache Kafka, Spark for processing, and Streamlit for visualization**.

## Database Schema
![Database_Design](images/database_design.png)
- Candidate: contains candidates information (candidate_id, name, age, dob, gender, first_name, last_name, party, image_url, is_active)
- Voter: contains voters information (voter_id, name, age, dob, gender, state, email, phone)
- Vote: contains vote information (vote_id, voter_id, candidate_id, voted_at)

## API
Voters information are gotton from Random User API: https://randomuser.me/

```bash Example
import requests

# Basic request - gets one random user
response = requests.get('https://randomuser.me/api/')
user = response.json()

# Get multiple users (e.g., 5 users)
response = requests.get('https://randomuser.me/api/?results=5')
users = response.json()

# Get specific fields and nationalities
response = requests.get('https://randomuser.me/api/?nat=us,gb&results=3&gender=female')
# This gets 3 female users from US or GB

# Example of accessing the data
for user in users['results']:
    print(f"Name: {user['name']['first']} {user['name']['last']}")
    print(f"Email: {user['email']}")
    print(f"Location: {user['location']['city']}, {user['location']['country']}")
    print("---")
```
## Project Overview

The project consists of three main components:

## Features
- 🗳️ Real-time vote counting and visualization
- 🗺️ Interactive US map showing state-by-state results
- 📈 Time series vote tracking
- 📋 Detailed state-level voting table
- 🔄 Auto-refreshing data every 5 seconds

## Technologies Used

- **Python 3.9**
- **Apache Kafka & Zookeeper**: Message streaming
- **Apache Spark**: Data processing
- **PostgreSQL**: Database
- **Streamlit**: Dashboard interface
- **Pandas & NumPy**: Data manipulation
- **Docker & Docker Compose**: Containerization

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.9+](https://www.python.org/downloads/) (for local development)
- [Git](https://git-scm.com/downloads)

## Project Structure
```bash
Voting-Dashboard/
├── docs/
├── lib/
├── src/
│   ├── dashboard.py      # Streamlit dashboard
├── docker-compose.yml
├── requirements.txt
└── README.md
```
## Getting Started (Using Docker)


## Component Descriptions



## Dashboard Components
