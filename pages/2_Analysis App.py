import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Real Estate Analytics", layout="wide")

# -------------------- Load Data ---------------------
st.title('🏠 Real Estate Analytics Dashboard')

new_df = pd.read_csv('datasets/data_viz1.csv')
feature_text = pickle.load(open('datasets/feature_text.pkl','rb'))

cols_to_numeric = ['price','price_per_sqft','built_up_area','latitude','longitude']
for col in cols_to_numeric:
    new_df[col] = pd.to_numeric(new_df[col], errors='coerce')

# ----------------- Dataset Overview -----------------
with st.expander("Dataset Overview"):
    st.write("Shape of dataset:", new_df.shape)
    st.write("First 5 rows:")
    st.dataframe(new_df.head())
    st.write("Null values:")
    st.dataframe(new_df.isnull().sum())

# ------------------- KPI Cards ----------------------
st.subheader("Key Insights")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average Price (in Cr)", f"₹ {new_df['price'].mean():.2f} Cr")
with col2:
    st.metric("Most Expensive Sector", new_df.groupby('sector')['price'].mean().idxmax())
with col3:
    st.metric("Most Common BHK", new_df['bedRoom'].mode()[0])

# ----------------- Interactive Filters -----------------
st.sidebar.header("Filter Data")
sector_filter = st.sidebar.selectbox("Select Sector", ['All'] + sorted(new_df['sector'].dropna().unique().tolist()))
bhk_filter = st.sidebar.selectbox("Select BHK", ['All'] + sorted(new_df['bedRoom'].dropna().unique().astype(int).tolist()))
property_type_filter = st.sidebar.selectbox("Property Type", ['All', 'house', 'flat'])

df_filtered = new_df.copy()
if sector_filter != 'All':
    df_filtered = df_filtered[df_filtered['sector'] == sector_filter]
if bhk_filter != 'All':
    df_filtered = df_filtered[df_filtered['bedRoom'] == int(bhk_filter)]
if property_type_filter != 'All':
    df_filtered = df_filtered[df_filtered['property_type'] == property_type_filter]

# ------------------ Map Visualization ------------------
st.header('Sector Price per Sqft Geomap')
group_df = df_filtered[['price', 'price_per_sqft', 'built_up_area', 'latitude', 'longitude', 'sector']].groupby('sector').mean()

fig = px.scatter_mapbox(group_df, lat="latitude", lon="longitude", color="price_per_sqft", size='built_up_area',
                        color_continuous_scale=px.colors.cyclical.IceFire, zoom=10,
                        mapbox_style="open-street-map", width=1200, height=700, hover_name=group_df.index)

st.plotly_chart(fig, use_container_width=True)

# -------------------- Wordcloud ----------------------
st.header(' Features Wordcloud')
wordcloud = WordCloud(width=800, height=800, background_color='black',
                      stopwords=set(['s']), min_font_size=10).generate(feature_text)

fig_wc = plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=0)
st.pyplot(fig_wc)

# -------------------- Scatter Plot -------------------


st.header(' Area vs Price by BHK')
fig1 = px.scatter(df_filtered, x="built_up_area", y="price", color="bedRoom",
                  title="Area vs Price", labels={"bedRoom": "BHK"})
st.plotly_chart(fig1, use_container_width=True)

# -------------------- BHK Pie Chart ------------------


st.header(' BHK Distribution')
fig2 = px.pie(df_filtered, names='bedRoom', title='BHK Pie Chart')
st.plotly_chart(fig2, use_container_width=True)

# ------------------ Boxplot Comparison ---------------


st.header('BHK Price Comparison (≤4 BHK)')
fig3 = px.box(df_filtered[df_filtered['bedRoom'] <= 4], x='bedRoom', y='price', title='Price Range by BHK')
st.plotly_chart(fig3, use_container_width=True)

# ----------------- Distplot for Price ---------------


st.header('Price Distribution by Property Type')
fig4 = plt.figure(figsize=(10, 4))
sns.histplot(df_filtered[df_filtered['property_type'] == 'house']['price'], label='house', kde=True)
sns.histplot(df_filtered[df_filtered['property_type'] == 'flat']['price'], label='flat', kde=True)
plt.legend()
st.pyplot(fig4)

# ------------------ Barplot by Sector ----------------


st.header(' Avg Price per Sector')
fig5 = px.bar(df_filtered.groupby('sector')['price'].mean().reset_index(),
              x='sector', y='price', title='Avg Price by Sector')
st.plotly_chart(fig5, use_container_width=True)

# -------------------- Download -----------------------

st.subheader("Download Filtered Dataset")
st.download_button("Download CSV", df_filtered.to_csv(index=False), "filtered_data.csv", "text/csv")










