import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import altair as alt
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh
import geopandas as gpd

# Set page config
st.set_page_config(
    page_title="Real-time Voting Dashboard",
    layout="wide"
)

# Auto refresh every 30 seconds
st_autorefresh(interval=30000, limit=None, key="refresh")

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


def get_gender_division():
    conn = connect_to_db()
    query = """
    SELECT v.gender, COUNT(*) as vote_count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM vote), 2) as percentage
    FROM vote vt
    JOIN voter v ON vt.voter_id = v.voter_id
    GROUP BY v.gender
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_votes_by_state():
    conn = connect_to_db()
    query = """
    SELECT 
        v.address_state, 
        COUNT(*) as vote_count,
        string_agg(DISTINCT c.party, ', ') as party
    FROM vote vt
    JOIN voter v ON vt.voter_id = v.voter_id
    JOIN candidate c ON vt.candidate_id = c.candidate_id
    GROUP BY v.address_state
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_leading_candidate_by_state():
    conn = connect_to_db()
    query = """
    WITH state_party_votes AS (
        SELECT 
            v.address_state,
            c.party,
            COUNT(*) as party_votes,
            RANK() OVER (PARTITION BY v.address_state ORDER BY COUNT(*) DESC) as rank
        FROM vote vt
        JOIN voter v ON vt.voter_id = v.voter_id
        JOIN candidate c ON vt.candidate_id = c.candidate_id
        GROUP BY v.address_state, c.party
    )
    SELECT 
        address_state,
        party,
        party_votes
    FROM state_party_votes
    WHERE rank = 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_age_distribution():
    conn = connect_to_db()
    query = """
    SELECT 
        CASE 
            WHEN age < 30 THEN '18-29'
            WHEN age < 45 THEN '30-44'
            WHEN age < 60 THEN '45-59'
            ELSE '60+'
        END as age_group,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
    FROM vote vt
    JOIN voter v ON vt.voter_id = v.voter_id
    GROUP BY 
        CASE 
            WHEN age < 30 THEN '18-29'
            WHEN age < 45 THEN '30-44'
            WHEN age < 60 THEN '45-59'
            ELSE '60+'
        END
    ORDER BY age_group;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_state_details():
    conn = connect_to_db()
    query = """
    SELECT 
        v.address_state,
        c.party,
        COUNT(*) as vote_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY v.address_state), 2) as percentage,
        COUNT(DISTINCT vt.voter_id) as total_voters,
        ROUND(AVG(v.age), 1) as avg_age,
        COUNT(CASE WHEN v.gender = 'male' THEN 1 END) * 100.0 / COUNT(*) as male_percentage
    FROM vote vt
    JOIN voter v ON vt.voter_id = v.voter_id
    JOIN candidate c ON vt.candidate_id = c.candidate_id
    GROUP BY v.address_state, c.party
    ORDER BY v.address_state, vote_count DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    st.title('🗳️ Real-time Voting Dashboard')
    st.write("Live voting results updated every 30 seconds")

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

    st.markdown("---")  # Add divider
    st.subheader('Vote Distribution by State')
    
    # Create two columns for maps
    map_col1, map_col2 = st.columns(2, gap="medium")

    with map_col1:
        st.write("Total Votes by State")
        votes_by_state_df = get_votes_by_state()
        
        us_states = gpd.read_file('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
        merged_data = us_states.merge(votes_by_state_df, left_on='name', right_on='address_state', how='left')
        
        fig1 = px.choropleth(merged_data, 
                          geojson=merged_data.geometry, 
                          locations=merged_data.index, 
                          color='vote_count',
                          color_continuous_scale="Viridis",
                          hover_name="name",
                          hover_data=["party", "vote_count"])

        fig1.update_geos(fitbounds="locations", visible=False)
        fig1.update_layout(height=600,  # Increased from 400 to 600
                          margin={"r":0,"t":0,"l":0,"b":0},
                          width=800)  # Added width
        st.plotly_chart(fig1, use_container_width=True)

    with map_col2:
        st.write("Leading Party by State")
        leading_party_df = get_leading_candidate_by_state()
        
        merged_party_data = us_states.merge(leading_party_df, 
                                          left_on='name', 
                                          right_on='address_state', 
                                          how='left')
        
        fig2 = px.choropleth(merged_party_data, 
                          geojson=merged_party_data.geometry, 
                          locations=merged_party_data.index, 
                          color='party',
                          color_discrete_map=PARTY_COLORS,
                          hover_name="name",
                          hover_data=["party", "party_votes"])

        fig2.update_geos(fitbounds="locations", visible=False)
        fig2.update_layout(height=600,  # Increased from 400 to 600
                          margin={"r":0,"t":0,"l":0,"b":0},
                          width=800)  # Added width
        st.plotly_chart(fig2, use_container_width=True)

    # Gender division of voters
    st.subheader('Gender Division of Voters')
    gender_data = get_gender_division()
    
    fig = px.pie(gender_data, values='percentage', names='gender', title='Gender Division of Voters (%)')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    # Age Distribution
    st.subheader("Voter Age Distribution")
    age_data = get_age_distribution()
    
    # Bar chart for age distribution
    age_chart = alt.Chart(age_data).mark_bar().encode(
        x=alt.X('age_group:O', title='Age Group'),
        y=alt.Y('count:Q', title='Number of Votes'),
        color=alt.Color('count:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['age_group', 'count', 'percentage']
    ).properties(height=300)
    
    st.altair_chart(age_chart, use_container_width=True)

    # State-level Analysis
    st.subheader("State-level Voting Analysis")
    state_data = get_state_details()
    
    # State selector
    selected_state = st.selectbox(
        "Select a state to view details",
        options=sorted(state_data['address_state'].unique())
    )
    
    # Filter data for selected state
    state_filtered = state_data[state_data['address_state'] == selected_state]
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_voters = state_filtered['total_voters'].iloc[0]
        st.metric("Total Voters", f"{total_voters:,}")
        
    with col2:
        avg_age = state_filtered['avg_age'].iloc[0]
        st.metric("Average Age", f"{avg_age:.1f}")
        
    with col3:
        male_pct = state_filtered['male_percentage'].iloc[0]
        st.metric("Male/Female Ratio", f"{male_pct:.1f}% / {100-male_pct:.1f}%")

    # Party distribution for selected state
    party_chart = alt.Chart(state_filtered).mark_bar().encode(
        x=alt.X('party:N', title='Party'),
        y=alt.Y('vote_count:Q', title='Votes'),
        color=alt.Color('party:N', scale=alt.Scale(domain=list(PARTY_COLORS.keys()),
                                                  range=list(PARTY_COLORS.values()))),
        tooltip=['party', 'vote_count', 'percentage']
    ).properties(height=300)
    
    st.altair_chart(party_chart, use_container_width=True)

    # Create expandable details section
    with st.expander("View Detailed State Statistics"):
        st.dataframe(
            state_filtered[['party', 'vote_count', 'percentage']]
            .sort_values('vote_count', ascending=False)
        )

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
