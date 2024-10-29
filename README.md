# Real Time Election Voting System
This repository is part of our group project for DS5110. We have chosen to develop a scalable, real-time voting system using big data technologies. We'll incorporate technologies like Docker, Kafka, PostgreSQL, Python, Apache Spark, and Streamlit to build a robust, scalable, live-updating voting platform.

## System Architecture
(need a diagram)
 The system processes votes in real-time using **Apache Kafka, Spark for processing, and Streamlit for visualization**.

## Database Schema
(need a diagram)
Candidate: contains candidates information (candidate_id, name, age, dob, gender, first_name, last_name, party, image_url, is_active)
Voter: contains voters information (voter_id, name, age, dob, gender, state, email, phone)
Vote: contains vote information (vote_id, voter_id, candidate_id, voted_at)

## API
Voters information are gotton from Random User API: https://randomuser.me/
(short explanations how to use this API)

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
