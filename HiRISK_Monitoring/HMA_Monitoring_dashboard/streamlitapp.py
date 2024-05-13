import streamlit as st 
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go 
import geojson 
@st.cache_resource
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def get_gj(): 
    with open('HiRISK_Monitoring/HMA_Monitoring_dashboard/HIMAP_boundaries.geojson') as f:
        gj = geojson.load(f)
    return gj


st. set_page_config(layout="wide")

mapbox_access_token = "pk.eyJ1IjoiYW1hbnp5MTIzNCIsImEiOiJjbG9land0NjcwazR6MmtvMjgycTJ2bHp2In0.wEKHMlZHua7rHUV0Av03UQ"
px.set_mapbox_access_token(mapbox_access_token)
st.title("HiRisk Monitoring")
st.divider()

df = pd.read_csv("HiRISK_Monitoring/HiRISKMonitoringDashboard_HMA.csv",encoding = 'latin1')

#Loop through columns
panel_text = ""
for column in df.columns:
    # Convert column values to string and concatenate with "<br>"
    panel_text +="<br>" + column + ": " + df[column].astype(str)


# df['text'] = "<br>HiRISKDB_ID: " + df["HiRISKDB_ID"].astype(str)+"<br>Name: " + df["Name"].astype(str)+"<br>Type: " + df["Type"].astype(str)+"<br>Category: " + df["Category"].astype(str)+"<br>Latitude: " + df["Latitude"].astype(str)+"<br>Longitude: " + df["Longitude"].astype(str)+"<br>min Elevation: " + df["min Elevation"].astype(str)+"<br>Elevation: " + df["Elevation"].astype(str)+"<br>max Elevation: " + df["max Elevation"].astype(str)+"<br>Country: " + df["Country"].astype(str)+"<br>Data owner/Data manager: " + df["Data owner/Data manager"].astype(str)+"<br>Manager email: " + df["Manager email"].astype(str)+"<br>Data Access Quality: " + df["Data Access Quality"].astype(str)+"<br>Data Access (URL): " + df["Data Access (URL)"].astype(str)+"<br>Data Publication: " + df["Data Publication"].astype(str)+"<br>Activity: " + df["Activity"].astype(str)+"<br>Physical Variables: " + df["Physical Variables"].astype(str)+"<br>Socioeconomic dimensions: " + df["Socioeconomic dimensions"].astype(str)+"<br>Hazard data: " + df["Hazard data"].astype(str)+"<br>Start Date: " + df["Start Date"].astype(str)+"<br>End Date: " + df["End Date"].astype(str)+"<br>Temporal frequency (highest): " + df["Temporal frequency (highest)"].astype(str)+"<br>Global network contribution: " + df["Global network contribution"].astype(str)
df['text'] = panel_text
variables = sorted(list(set(sorted([x.replace(" ", "") for x in list(set(",".join(df["Physical Variables"].unique().tolist()).strip().split(",")))]))))
selected_variables = st.multiselect("Select Variables", variables)



qualifying_rows = []
if (len(selected_variables)!=0):
    for row in df.iterrows():
        if set(set(selected_variables)).issubset(row[1]["Physical Variables"].replace(" ", "").split(",")):
            qualifying_rows.append(row[1])
    df = pd.DataFrame(qualifying_rows)


variable_descriptions = {
    "SD" : "Snow Depth", 
    "RH" : "Relative Humidity", 
    "SWE": "Snow Water Equivalent", 
    "GT": "Ground Temperature", 
    "Q" : "Discharge", 
    "W" : "Wind", 
    "P" : "Precipitation", 
    "T": "Temperature", 
    "RAD": "Radiation", 
    "ET": "Evapotranspiration"
}

for var in selected_variables: 
    if var in variable_descriptions.keys():
        st.write(f"***{var} - {variable_descriptions[var]}***")

st.divider()
if(df.shape[0] > 0):

     #Assign colors

    cmap = {"EWS": 'red', "Network": 'blue', "Single" : 'grey',"CS":'green'}   
    
    sequence = []
    for t in df["Type"].unique().tolist(): 
        sequence.append(cmap[t])
    fig = go.Figure(data=px.scatter_mapbox(
            df, 
            lon = df['Longitude'],
            lat = df['Latitude'],
            color = df['Type'],
            mapbox_style='light',
            color_discrete_sequence=sequence,
            hover_name=df['text']
            ))
    fig.update_layout(mapbox_layers=[{
                    "below": 'traces',
                    "sourcetype": "geojson",
                    "type": "line",
                    "color": "black",
                    "source": get_gj()
                }])

    fig.update_layout(
            autosize=True,
            hovermode='closest',
            # showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=36,
                    lon=85
                ),
                pitch=0,
                zoom=3.8,
                style='light'
            ),
                height = 650, 
                margin=dict(l=0,r=0,b=0,t=0)
        )
    st.plotly_chart(fig, use_container_width=True)
    temp_li = list(df.columns)
    temp_li.remove("text")
    st.dataframe(df[temp_li])
    # st.write(temp_li)
    csv = convert_df(df[temp_li])
    st.download_button(
            "Download Data",
            csv,
            f"Filtered Data.csv",
            "text/csv",
            key='download-csv'
    )
st.image("HiRISK_Monitoring/HMA_Monitoring_dashboard/logo_hirisk.png")
st.markdown("https://hirisk.org/")
