import streamlit as st
import requests
import plotly.express as px

# ----- Function to fetch data from LeetCode -----
def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/"
    }

    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
        profile {
          ranking
        }
      }
    }
    """

    payload = {
        "operationName": "getUserProfile",
        "variables": {"username": username},
        "query": query
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        try:
            user_data = data["data"]["matchedUser"]
            submissions = user_data["submitStatsGlobal"]["acSubmissionNum"]
            ranking = user_data["profile"]["ranking"]
            stats = {entry["difficulty"]: entry["count"] for entry in submissions if entry["difficulty"] != "All"}
            total = sum(stats.values())
            return stats, total, ranking
        except:
            return None, None, None
    else:
        return None, None, None

# ----- Streamlit UI -----
st.set_page_config(page_title="LeetCode Profile Viewer", page_icon="🐍", layout="centered")

st.markdown("<h1 style='text-align: center;'>📊 LeetCode Stats Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enter a LeetCode username to view their progress</p>", unsafe_allow_html=True)

with st.form(key="leetcode_form"):
    username = st.text_input("🔎 LeetCode Username", placeholder="e.g. johndoe")
    submit = st.form_submit_button("Get Stats")

if submit and username:
    with st.spinner("Fetching data..."):
        stats, total, rank = get_leetcode_stats(username.strip())

    if stats:
        st.success(f"✅ Stats found for **{username}**")
        
        # Metrics at the top
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="✅ Total Solved", value=total)
        with col2:
            st.metric(label="🏆 Global Rank", value=f"#{rank:,}" if rank else "N/A")

        # Pie chart
        fig = px.pie(
            names=list(stats.keys()),
            values=list(stats.values()),
            title="Problems by Difficulty",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

        # Raw Stats
        st.markdown("### 📋 Breakdown")
        for diff, count in stats.items():
            st.write(f"**{diff}:** {count}")
    else:
        st.error("❌ Could not retrieve data. Please check the username.")
