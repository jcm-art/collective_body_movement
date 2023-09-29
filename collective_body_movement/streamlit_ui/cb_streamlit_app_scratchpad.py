

import time

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


from collective_body_movement.datamanager.data_manager import CollectiveBodyDataManager


# Streamlit page configuration and formatting
st.set_page_config(layout="wide") # Removing this narrows to ~1/2 of screen
st.title("Colletive Body Movement")

# Define an expander at the top to provide more information for the app
with st.expander("About this app"):
    st.write('This app allows the user to view and analyze movement logs from actors in the Collective Body work. For more information, visit https://www.sarahsilverblatt.com/about')


# Load datasets and metrics

# TODO (jcm-art): Prevent database reload with every page option selection
cbdm = CollectiveBodyDataManager(
    database_directory="data/movement_database/", 
    metrics_directory="data/movement_database/")


# Select Dataset,  Participant ID, and Metric for visualization
st.header("Select a Dataset and Paricipant ID")
dataset_options = cbdm.get_session_IDs()
# TODO (jcm-art): update options for participant ID based on dataset selection
user_dataset_selection = st.selectbox(
    label="Select a dataset ID",
    options=dataset_options,
)

headset_options = cbdm.get_actor_IDs(user_dataset_selection)
user_headset_selection = st.selectbox(
    label="Select a participant ID",
    options=headset_options,
)

metric_options = cbdm.get_metric_options()
user_metric_selection = st.selectbox(
    label="Select a Metric",
    options=metric_options,
)

# Plot the selected dataset

st.header("Data plots")
st.subheader("Static Movement Chart")

movement_data_dictionary = cbdm.get_frame_dataset_dict(user_dataset_selection, user_headset_selection, normalize=True, chapter_range=[1,3])
movement_df = movement_data_dictionary["dataset"]
st.write(movement_df)

c = alt.Chart(movement_df).mark_point().encode(
    x=alt.X('head_pos_y', scale=alt.Scale(domain=[0, 1])),
    y=alt.Y('head_pos_z', scale=alt.Scale(domain=[0, 1])), 
    color='chapitre:N',
    tooltip=['head_pos_y','head_pos_z']
).properties(
    width=1000,
    height=1000
)
st.write(c)


st.header("Tailed animated movement")

user_dataset_selection_path = st.selectbox("Which dataset would you like to view for the path animation?", dataset_options, index=0)
headset_options = cbdm.get_actor_IDs(user_dataset_selection)
user_headset_selection_path = st.selectbox("Which actor would you like to view for the path animation?", headset_options, index=0)
chapter_options = [1,2,3]
user_chapter_selection_path = st.selectbox("Which chapter would you like to see for the path animation?", chapter_options,index=0)

movement_data_dictionary = cbdm.get_frame_dataset_dict(user_dataset_selection_path, user_headset_selection_path, normalize=True, chapter_range=[1,3])
movement_df = movement_data_dictionary["dataset"]
chapter_df = movement_df[movement_df["chapitre"] == user_chapter_selection_path]

x = chapter_df["head_pos_x"].tolist()
y = chapter_df["head_pos_z"].tolist()
step=2
xx = x[0:-1:step]
yy = y[0:-1:step]
N = len(xx)

fig = go.Figure(
    data=[
        go.Scatter(
            x=x, 
            y=y, 
            mode="lines",
            line=dict(width=1, color="white", dash='dot')),
        go.Scatter(
            x=x, 
            y=y, 
            mode="lines",
            line=dict(width=1, color="white", dash='dot'))],
        layout=go.Layout(
            xaxis=dict(range=[0,1], autorange=False, zeroline=False),
            yaxis=dict(range=[0,1], autorange=False, zeroline=False),
            title_text="Actor Position", hovermode="closest",
            updatemenus=[dict(type="buttons",
                              buttons=[dict(label="Play",
                                            method="animate",
                                            args=[
                                                None, {"frame": {"duration": 15, "redraw": False},
                                                       "fromcurrent": True, 
                                                       "transition": {"duration": 10,"easing": "quadratic-in-out"}}],
                                            )])]),
        frames=[go.Frame(
            data=[go.Scatter(
                x=[xx[k]],
                y=[yy[k]],
                mode="markers",
                marker=dict(color="red", size=10))])
                
            for k in range(N)]
)
# TODO - add a slider (requires pregenerated frames)
# https://plotly.com/python/sliders/

st.write(fig)


st.header("Basic animated movement")

user_dataset_selection_basic = st.selectbox("Which dataset would you like to view for the basic animation?", dataset_options, index=0)
headset_options = cbdm.get_actor_IDs(user_dataset_selection)
user_headset_selection_basic = st.selectbox("Which actor would you like to view for the basic animation?", headset_options, index=0)

movement_data_dictionary = cbdm.get_frame_dataset_dict(user_dataset_selection_basic, user_headset_selection_basic, normalize=True, chapter_range=[1,3])
movement_df = movement_data_dictionary["dataset"]

fig = px.scatter(
    movement_df, 
    x="head_pos_x", 
    y="head_pos_z", 
    color="chapitre", 
    range_x=[0,1], range_y=[0,1],
    animation_frame="elapsed_time", 
    animation_group="chapitre",)

fig.update_layout(width=600, height=600)
fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 10

st.plotly_chart(fig, use_container_width=True)

'''
start_time = movement_df["timestamp"].min()
end_time = movement_df["timestamp"].max()
num_frames = 100
time_step = (end_time - start_time ) / num_frames

st.write(f"Time step: {time_step} for start time {start_time} and end time {end_time}")

partial_df =  movement_df.loc[(movement_df["timestamp"] <= start_time+time_step)]

animated_chart = alt.Chart(partial_df).mark_point().encode(
    x=alt.X('head_pos_y', scale=alt.Scale(domain=[0, 1])),
    y=alt.Y('head_pos_z', scale=alt.Scale(domain=[0, 1])), 
    color=alt.Color('elapsed_time:Q').legend(None),
    tooltip=['head_pos_y','head_pos_z']
).properties(
    width=700,
    height=700
)
st.write(animated_chart)

for i in range(0, 10):
    partial_df =  movement_df.loc[
        (movement_df["timestamp"] <= start_time+time_step) & 
        (movement_df["timestamp"] <= start_time+time_step)]
'''


'''
st.header("Animated plot example")


df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
def draw(df):
  chart = alt.Chart(df.reset_index()).transform_fold(df.columns.tolist(), as_=['quote', 'price']).mark_line().encode(x='index:T', y='price:Q')
  return chart

chart = draw(df)
realTimeChart = st.altair_chart(chart)

while True:
  df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
  chart = draw(df)
  realTimeChart = realTimeChart.altair_chart(chart)
  time.sleep(0.2)
  '''

'''
def draw(df):
    chart = alt.Chart(movement_df).mark_point().encode(
        x=alt.X('head_pos_y', scale=alt.Scale(domain=[0, 1])),
        y=alt.Y('head_pos_z', scale=alt.Scale(domain=[0, 1])), 
        color='chapitre:N',
        tooltip=['head_pos_y','head_pos_z']
    ).properties(
        width=800,
        height=800,
    )
    # chart = alt.Chart(df.reset_index()).transform_fold(df.columns.tolist(), as_=['quote', 'price']).mark_line().encode(x='index:T', y='price:Q')
    return chart

chart = draw(movement_df)
realTimeChart = st.altair_chart(chart)

while True:
  df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
  rt_chart = draw(df)
  realTimeChart = realTimeChart.altair_chart(rt_chart)
  time.sleep(0.2)'''
