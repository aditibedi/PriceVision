import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Set up the page
st.set_page_config(page_title="Recommend Apartments")

# Load data
location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))

# Recommender function
def recommend_properties_with_scores(property_name, top_n=5):
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]

    top_properties = location_df.index[top_indices].tolist()

    recommendations_df = pd.DataFrame({
        'PropertyName': top_properties,
        'SimilarityScore': top_scores
    })

    return recommendations_df

# --------------------------
# Section 1: Radius Filter
# --------------------------
st.title('🔍 Search Apartments by Location and Radius')

selected_location = st.selectbox('Choose a location:', sorted(location_df.columns.to_list()))

radius = st.number_input('Enter radius (in kms):', min_value=0.0, step=0.5)

if st.button('Search'):
    try:
        nearby_apartments = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()
        if nearby_apartments.empty:
            st.warning("No apartments found within the selected radius.")
        else:
            st.subheader("🏘️ Apartments within radius:")
            for apartment, distance in nearby_apartments.items():
                st.text(f"{apartment} - {round(distance / 1000, 2)} kms")
    except KeyError:
        st.error("Selected location not found in the dataset.")

# --------------------------
# Section 2: Recommendation
# --------------------------
st.title('🏡 Recommend Apartments')

selected_apartment = st.selectbox('Select an apartment to get recommendations:', sorted(location_df.index.to_list()))

if st.button('Recommend'):
    recommendation_df = recommend_properties_with_scores(selected_apartment)
    st.subheader(f"Top recommendations similar to '{selected_apartment}'")
    st.dataframe(recommendation_df)



