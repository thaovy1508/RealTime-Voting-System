import streamlit_autorefresh 
import streamlit as st
import psycopg2
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Database connection function
def connect_to_db():
    return psycopg2.connect(
        host="localhost",
        database="voting",
        user="postgres",
        password="postgres"
    )

# Function to get total votes
def get_total_votes():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM vote")
    total_votes = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total_votes

# Function to get votes by candidate
def get_votes_by_candidate():
    conn = connect_to_db()
    query = """
    SELECT c.first_name, c.last_name, c.party, COUNT(*) as vote_count
    FROM vote v
    JOIN candidate c ON v.candidate_id = c.candidate_id
    GROUP BY c.candidate_id, c.first_name, c.last_name, c.party
    ORDER BY vote_count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to get votes by location
def get_votes_by_location():
    conn = connect_to_db()
    query = """
    SELECT v.address_state, COUNT(*) as vote_count
    FROM vote vt
    JOIN voter v ON vt.voter_id = v.voter_id
    GROUP BY v.address_state
    ORDER BY vote_count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to get historical voting trends
def get_historical_trends():
    conn = connect_to_db()
    query = """
    SELECT DATE(voted_at) as vote_date, COUNT(*) as vote_count
    FROM vote
    GROUP BY DATE(voted_at)
    ORDER BY vote_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to get candidate information
def get_candidate_info():
    conn = connect_to_db()
    query = """
    SELECT first_name, last_name, party, age, gender, biography, img_url
    FROM candidate
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit app
st.title('Real-time Voting Dashboard')

# Display total votes
total_votes = get_total_votes()
st.metric("Total Votes Cast", total_votes)

# Display votes by candidate
st.subheader('Votes by Candidate')
candidate_data = get_votes_by_candidate()
candidate_chart = alt.Chart(candidate_data).mark_bar().encode(
    x=alt.X('vote_count:Q', title='Votes'),
    y=alt.Y('first_name:N', title='Candidate', sort='-x'),
    color='party:N',
    tooltip=['first_name', 'last_name', 'party', 'vote_count']
).properties(
    width=600,
    height=300
)
st.altair_chart(candidate_chart, use_container_width=True)

# Display votes by location
st.subheader('Votes by Location')
location_data = get_votes_by_location()
location_chart = alt.Chart(location_data).mark_arc().encode(
    theta='vote_count:Q',
    color='address_state:N',
    tooltip=['address_state', 'vote_count']
).properties(
    width=400,
    height=400
)
st.altair_chart(location_chart, use_container_width=True)

# Display historical trends
st.subheader('Historical Voting Trends')
trends_data = get_historical_trends()
trends_chart = alt.Chart(trends_data).mark_line().encode(
    x='vote_date:T',
    y='vote_count:Q',
    tooltip=['vote_date', 'vote_count']
).properties(
    width=600,
    height=300
)
st.altair_chart(trends_chart, use_container_width=True)

# Display candidate information
st.subheader('Candidate Information')
candidate_info = get_candidate_info()
for _, candidate in candidate_info.iterrows():
    with st.expander(f"{candidate['first_name']} {candidate['last_name']} ({candidate['party']})"):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(candidate['img_url'], width=150)
        with col2:
            st.write(f"**Age:** {candidate['age']}")
            st.write(f"**Gender:** {candidate['gender']}")
            st.write(f"**Biography:** {candidate['biography']}")

# Auto-refresh the app every 30 seconds
st1.experimental_rerun()