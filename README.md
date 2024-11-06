# Real Time Election Voting System
This repository is part of our group project for DS5110. We have chosen to develop a scalable, real-time voting system using big data technologies. We'll incorporate technologies like **Docker, Kafka, PostgreSQL, Python, Apache Spark, and Streamlit** to build a robust, scalable, live-updating voting platform. The system uses Docker Compose to quickly set up the needed services in Docker containers.

## System Architecture
![System_Architecture](images/system_architecture.png)
- The system processes votes in real-time using **PostgreSQL for storage**, **Apache Kafka, Spark for processing, and Streamlit for visualization**.

## Database Schema
![Database_Design](images/database_design.png)
- **Candidate**: contains candidates information (**candidate_id**, dob, age, gender, first_name, last_name, biography, party, image_url)
- **Voter**: contains voters information (**voter_id**, dob, age, gender,registration_number, first_name, last_name, nationality, address, email, phone)
- **Vote**: contains vote information (**vote_id**, voter_id, candidate_id, voted_at)

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
- [Anaconda](https://www.anaconda.com/download) (for virtual environment)
- [PostgreSQL](https://www.postgresql.org/download/)

## Project Structure
```bash
Voting-Dashboard/
├── docs/
├── images/
├── lib/
├── src/
│   ├── dashboard.py      # Streamlit dashboard
├── docker-compose.yml
├── requirements.txt
└── README.md
```
## Getting Started (Using Docker & Anaconda)
**1. Setting up Environment file**
- Open Anaconda Prompt
- Navidate to your project directory
```bash
# Create the environment from the file
conda env create -f environment.yml

# Activate the environment
conda activate voting-system

# To deactivate an active environment, use
conda deactivate
```
- If you need to update the environment later
```bash
# After adding new packages to environment.yml
conda env update -f environment.yml --prune
```

**2. Setting up Docker Service**
- Make sure Docker Desktop is running first (you need to start Docker Desktop application)
- Open Anaconda Prompt and navigate to your project directory
```bash
# Start all services
docker-compose up -d

# Create topics
docker exec -it voting_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic voters_topic --partitions 1 --replication-factor 1

docker exec -it voting_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic candidates_topic --partitions 1 --replication-factor 1

docker exec -it voting_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic votes_topic --partitions 1 --replication-factor 1

docker exec -it voting_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic aggregated_votes_per_candidate --partitions 1 --replication-factor 1

docker exec -it voting_kafka kafka-topics --create --bootstrap-server localhost:9092 --topic aggregated_turnout_by_location --partitions 1 --replication-factor 1

# Verify topics were created
docker exec -it voting_kafka kafka-topics --list --bootstrap-server localhost:9092

# To stop services 
docker-compose down

# To restart services
docker-compose restart

# Remove everything including volumes (clean start)
docker-compose down -v

```

**3. Verify PostgreSQL**
```bash
# Connect to PostgreSQL
docker exec -it voting_postgres psql -U postgres -d voting

# You should see the PostgreSQL prompt: voting=#
# Type \q to exit

# Restart PostgreSQL if needed
docker-compose restart postgres

# Check PostgreSQL logs
docker log voting_postgres

```
**4. Set up database**
```bash
# Make sure your conda environment is activated
conda activate voting-system

# Run the setup script
python src/setup_database.py

```

**5. Run voting simulator**
```bash
# Make sure your conda environment is activated

# Run the simulator script
python src/data_generator.py

# This file will generate data indefinitely, to stop the process press "Ctrl-C"
```
**6. Run analytics**

**7. Run Streamlit Dashboard**

## Component Descriptions
### **1.setup_database.py**
This file will connect to PostgreSQL database, create "vote", "voter", "candidate" databases.

**Key Features:**

Schema Management
    - Table creation for voter, candidate, and vote tables
    - Index creation for performance optimization
    - Foreign key constraints for data integrity
    - Data type validation

Database Operations
    - CRUD operations setup
    - Transaction management
    - Database migration capabilities

### **2. data_generator.py**
This fill will generate data from RandomUser API as voting simulator, and inserted the data to the database accordingly.

**Key Features:**

Data Generation
    - Voter data generation
    - Candidate profile creation
    - Voting pattern simulation
    - Time-based vote distribution

Kafka Integration
    - Message production to Kafka topics
    - Message serialization and deserialization
    - Delivery confirmation handling

## Dashboard Components
