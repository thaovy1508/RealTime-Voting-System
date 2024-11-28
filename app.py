import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import altair as alt
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

# Set page config
st.set_page_config(
    page_title="Real-time Voting Dashboard",
    layout="wide"
)

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, limit=None, key="refresh")

# Define consistent colors for parties/candidates
PARTY_COLORS = {
    'Liberation Party': '#0072C6',    # Blue
    'United Republic Party': '#FF4444',  # Red
    'Management Party': '#87CEEB'     # Light Blue
}

# Keep your original functions
def connect_to_db():
    return psycopg2.connect(
        host="localhost",
        database="voting",
        user="postgres",
        password="postgres"
    )

def get_total_votes():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), MAX(voted_at) FROM vote")
    result = cur.fetchone()
    total_votes = result[0]
    last_update = result[1]
    cur.close()
    conn.close()
    return total_votes, last_update

def get_votes_by_candidate():
    conn = connect_to_db()
    query = """
    SELECT 
        c.first_name, 
        c.last_name, 
        c.party, 
        COUNT(*) as vote_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vote), 2) as percentage
    FROM vote v
    JOIN candidate c ON v.candidate_id = c.candidate_id
    GROUP BY c.candidate_id, c.first_name, c.last_name, c.party
    ORDER BY vote_count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_historical_trends():
    conn = connect_to_db()
    query = """
    WITH cumulative_votes AS (
        SELECT 
            c.first_name || ' ' || c.last_name as candidate_name,
            c.party,
            v.voted_at,
            COUNT(*) OVER (
                PARTITION BY c.candidate_id 
                ORDER BY v.voted_at
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) as cumulative_votes
        FROM vote v
        JOIN candidate c ON v.candidate_id = c.candidate_id
        ORDER BY v.voted_at
    )
    SELECT 
        DATE_TRUNC('minute', voted_at) as vote_time,
        candidate_name,
        party,
        MAX(cumulative_votes) as total_votes
    FROM cumulative_votes
    GROUP BY DATE_TRUNC('minute', voted_at), candidate_name, party
    ORDER BY vote_time;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_candidate_info():
    conn = connect_to_db()
    query = """
    SELECT first_name, last_name, party, age, gender, biography, img_url
    FROM candidate
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_leading_candidate():
    conn = connect_to_db()
    query = """
    SELECT 
        c.first_name, 
        c.last_name, 
        c.party, 
        COUNT(*) as vote_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vote), 2) as percentage
    FROM vote v
    JOIN candidate c ON v.candidate_id = c.candidate_id
    GROUP BY c.candidate_id, c.first_name, c.last_name, c.party
    ORDER BY vote_count DESC
    LIMIT 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

def get_active_locations():
    """Get count of states that have votes"""
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(DISTINCT v.address_state) 
        FROM vote vt
        JOIN voter v ON vt.voter_id = v.voter_id
    """)
    active_states = cur.fetchone()[0]
    cur.close()
    conn.close()
    return active_states

def main():
    st.title('🗳️ Real-time Voting Dashboard')
    st.write("Live voting results updated every 5 seconds")

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data
    total_votes, last_update = get_total_votes()
    leading_candidate = get_leading_candidate()
    active_states = get_active_locations()
    votes_by_candidate = get_votes_by_candidate()

    with col1:
        st.metric("Total Votes Cast", f"{total_votes:,}")
    
    with col2:
        if leading_candidate is not None:
            # Create two-line display with name and party
            name_display = leading_candidate['first_name'] + " " + leading_candidate['last_name']
            party_display = f"({leading_candidate['party']})"
            st.metric(
                "Leading Candidate",
                name_display,  # Main value shows just the name
                party_display  # Delta shows the party
            )
            # Add vote count and percentage below
            st.write(f"{leading_candidate['vote_count']} votes ({leading_candidate['percentage']}%)")

    with col3:
        st.metric("Active States", f"{active_states}", 
                 "Currently Voting")
    
    with col4:
        current_time = datetime.now().strftime('%H:%M:%S')
        current_date = datetime.now().strftime('%Y-%m-%d')
        st.metric("Last Updated", current_time, current_date)

    # Charts row - make them equal width
    st.markdown("---")  # Add divider
    col1, col2 = st.columns(2, gap="medium")  # Specify gap between columns

    # Vote Distribution by Party
    with col1:
        st.subheader('Vote Distribution by Party')
        party_data = votes_by_candidate.groupby('party')['vote_count'].sum().reset_index()
        fig = px.pie(party_data,
                    values='vote_count',
                    names='party',
                    hole=0.3,
                    color='party',
                    color_discrete_map=PARTY_COLORS)
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(
            height=350,
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True  
        )
        st.plotly_chart(fig, use_container_width=True)

    # Votes by Candidate
    with col2:
        st.subheader('Votes by Candidate')
        bar_chart = alt.Chart(votes_by_candidate).mark_bar().encode(
            x=alt.X('vote_count:Q', title='Number of Votes'),
            y=alt.Y('first_name:N', title='Candidate', sort='-x'),
            color=alt.Color('party:N', 
                          legend=None,  
                          scale=alt.Scale(domain=list(PARTY_COLORS.keys()),
                                        range=list(PARTY_COLORS.values()))),
            tooltip=['first_name', 'last_name', 'party', 'vote_count', 'percentage']
        ).properties(height=400)
        st.altair_chart(bar_chart, use_container_width=True)


    # Historical trends
    st.subheader('Cumulative Votes Over Time')
    trends_data = get_historical_trends()
    
    trends_chart = alt.Chart(trends_data).mark_line(point=True).encode(
        x=alt.X('vote_time:T', title='Time'),
        y=alt.Y('total_votes:Q', title='Total Votes'),
        color=alt.Color('party:N', 
                       legend=alt.Legend(orient='top'),  # Remove legend
                       scale=alt.Scale(domain=list(PARTY_COLORS.keys()),
                                     range=list(PARTY_COLORS.values()))),
        tooltip=['vote_time', 'candidate_name', 'party', 'total_votes']
    ).properties(
        height=400
    ).configure_axis(
        gridColor='lightgray',
        gridOpacity=0.3
    ).configure_point(
        size=50
    )
    
    st.altair_chart(trends_chart, use_container_width=True)

    # Candidate information
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


if __name__ == "__main__":
    main()