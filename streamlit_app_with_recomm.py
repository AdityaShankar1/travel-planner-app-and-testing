import streamlit as st
import requests
import pandas as pd
import recommender
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Travel Planner", page_icon="🧭", layout="centered")
st.title("🧭 Travel Planner")

# Sidebar filters
st.sidebar.header("Filters")
type_filter = st.sidebar.selectbox("Trip type", ["All", "solo", "group"])

# --- Create form ---
st.header("➕ Add a Travel Plan")
with st.form("create_plan"):
    name = st.text_input("Name")
    ttype = st.selectbox("Type", ["solo", "group"])
    destination = st.text_input("Destination")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Save")

    if submitted:
        payload = {
            "name": name,
            "type": ttype,
            "destination": destination,
            "notes": notes
        }
        r = requests.post(f"{API_URL}/plans", json=payload)
        if r.ok:
            st.success("Plan created!")
        else:
            st.error(f"Error: {r.status_code} {r.text}")

# --- List plans ---
st.header("📋 Your Plans")
param = {} if type_filter == "All" else {"type": type_filter}
resp = requests.get(f"{API_URL}/plans", params=param)

if resp.ok:
    plans = resp.json()
    if plans:
        df = pd.DataFrame(plans, columns=["id", "name", "type", "destination", "notes"])
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Plans as CSV", csv, "plans.csv", "text/csv")

        st.subheader("✏️ Manage Plans")
        for p in plans:
            with st.expander(f"{p[1]} — {p[3]} ({p[2]})"):
                new_name = st.text_input("Name", p[1], key=f"name-{p[0]}")
                new_type = st.selectbox("Type", ["solo", "group"],
                                        index=0 if p[2] == "solo" else 1,
                                        key=f"type-{p[0]}")
                new_dest = st.text_input("Destination", p[3], key=f"dest-{p[0]}")
                new_notes = st.text_area("Notes", p[4] or "", key=f"notes-{p[0]}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update #{p[0]}", key=f"update-{p[0]}"):
                        updates = {
                            "name": new_name,
                            "type": new_type,
                            "destination": new_dest,
                            "notes": new_notes
                        }
                        u = requests.put(f"{API_URL}/plans/{p[0]}", json=updates)
                        if u.ok:
                            st.success("Updated successfully")
                            st.experimental_rerun()
                        else:
                            st.error(f"Update failed: {u.status_code}")

                with col2:
                    if st.button(f"Delete #{p[0]}", key=f"delete-{p[0]}"):
                        d = requests.delete(f"{API_URL}/plans/{p[0]}")
                        if d.status_code == 204:
                            st.success("Deleted successfully")
                            st.experimental_rerun()
                        else:
                            st.error(f"Delete failed: {d.status_code}")
    else:
        st.info("No plans yet. Create one above.")
else:
    st.error("API unavailable. Is FastAPI running?")

# --- Popular Destinations Reference ---
st.header("🌍 Popular Destinations")

@st.cache_data
def load_destinations():
    return pd.read_csv("IndiaTourism.csv")

dest_df = load_destinations()
sample = dest_df.sample(5)

for _, row in sample.iterrows():
    st.subheader(f"{row['Name']} ({row['City']}, {row['State']})")
    st.write(f"🏷️ Type: {row['Type']}")
    st.write(f"⭐ Rating: {row['Google review rating']}")
    st.write(f"💰 Fee: {row['Entrance Fee in INR']} INR")
    st.write(f"🕒 Best Time: {row['Best Time to visit']}")


# --- Recommender System ---
st.header("🎶 Music Vibe → Travel Recommendation")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #e6ffe6; /* light green */
        color: black; /* force text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)
genre = st.radio(
    "Pick your favorite genre:",
    ["acoustic", "pop", "rock", "classical", "jazz", "hip hop"]
)

if st.button("Recommend Places"):
    recs = recommender.recommend_places(genre)
    for _, row in recs.iterrows():
        st.subheader(f"{row['Name']} ({row['City']}, {row['State']})")
        st.write(f"🏷️ Type: {row['Type']}")
        st.write(f"⭐ Rating: {row['Google review rating']}")
        st.write(f"💰 Fee: {row['Entrance Fee in INR']} INR")
        st.write(f"🕒 Best Time: {row['Best Time to visit']}")
        st.write("---")
