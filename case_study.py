#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 22:13:52 2023

@author: mac
"""

import csv
import pandas as pd
import numpy as np
import plotly.express as px
import re
import json
import streamlit as st
from streamlit_option_menu import option_menu
st.set_page_config(layout="wide")

pd.options.plotting.backend = "plotly"

file_path = ''
spotify=pd.read_csv(file_path+'spotify.csv', encoding='latin-1')

spotify['artists_name']=spotify['artists_name'].str.replace("\x96","ñ")
spotify['artists_name']=spotify['artists_name'].str.replace("Â","")
spotify['artists_name']=spotify['artists_name'].str.replace("\x92","í")
spotify['artists_name']=spotify['artists_name'].str.replace("\x97","ó")
spotify['artists_name']=spotify['artists_name'].str.replace("¬","")
spotify['artists_name']=spotify['artists_name'].str.replace("Â","")
spotify['artists_name']=spotify['artists_name'].str.replace("\x90","ê")
spotify['artists_name']=spotify['artists_name'].str.replace("\x91","ë")
spotify['artists_name']=spotify['artists_name'].str.replace("\x8b","ã")
spotify['artists_name']=spotify['artists_name'].str.replace("\x8d","ç")
spotify['artists_name']=spotify['artists_name'].str.replace("\x9f","ü")
spotify['artists_name']=spotify['artists_name'].str.replace("\x8e","é")
spotify['track_name']=spotify['track_name'].str.replace("\x96","ñ")
spotify['track_name']=spotify['track_name'].str.replace("Â","")
spotify['track_name']=spotify['track_name'].str.replace("\x92","í")
spotify['track_name']=spotify['track_name'].str.replace("\97","ó")
spotify['track_name']=spotify['track_name'].str.replace("\x90","ê")
spotify['track_name']=spotify['track_name'].str.replace("\x91","ë")
spotify['track_name']=spotify['track_name'].str.replace("\x8b","ã")
spotify['track_name']=spotify['track_name'].str.replace("\x8d","ç")
spotify['track_name']=spotify['track_name'].str.replace("\x9f","ü")
spotify['track_name']=spotify['track_name'].str.replace("\x8e","é")


date_cols = spotify[['released_year','released_month','released_day']]
spotify['released_date'] = pd.to_datetime(date_cols.rename(columns={'released_year':'year', 'released_month':'month', 'released_day':'day'}))
spotify['day_of_week'] = spotify['released_date'].dt.day_name()
spotify['month_name'] = spotify['released_date'].dt.month_name()

def label(element):
    if element >= 65:
        return 'High'
    elif element >= 40:
        return 'Decent'
    else:
        return 'Low'

spotify['danceability_level'] = spotify['danceability_percentage_value'].map(label)
spotify['valence_level'] = spotify['valence_percentage_value'].map(label)
spotify['energy_level'] = spotify['energy_percentage_value'].map(label)
spotify['acousticness_level'] = spotify['acousticness_percentage_value'].map(label)
spotify['liveness_level'] = spotify['liveness_percentage_value'].map(label)
spotify['speechiness_level'] = spotify['speechiness_percentage_value'].map(label)

spotify["artist_count_precise"]=spotify["artist_count"]
spotify.loc[spotify["artist_count"]>=4,"artist_count"]=-4

spotify["artist_count"]=spotify["artist_count"].astype(str)
spotify["artist_count"]=spotify["artist_count"].str.replace("-4","4+")

mask_0 = spotify['streams']==0
spotify.loc[:,'streams'] = spotify['streams'].mask(mask_0, spotify['streams'].mean().round())

spotify_graph=spotify.copy()
spotify_graph["artist_count"]=spotify_graph["artist_count"].astype("category")
spotify_graph["released_month"]=spotify_graph["released_month"].astype("category")
spotify_graph["released_year_category"]=spotify_graph["released_year"].astype("category")


spotify_artists = spotify_graph.copy()
artist_str = spotify['artists_name'].str.split(", ")
spotify_artists['artists_name'] = artist_str
spotify_artists = spotify_artists.explode('artists_name').reset_index(drop=True)


grouped = spotify_artists.groupby('artists_name')
streams_grouped = grouped['streams']
streams_s = streams_grouped.agg('sum')
top_artists_list = list(streams_s.sort_values(ascending=False).index)
top_15_artists = list(streams_s.sort_values(ascending=False).head(15).index)



color_list=["#ff0000","#663300","#00ffff","#0000ff","#ccff33","#000000","#ff8080","#ff6600","#ffff00","#ff9999","#8080ff","#00ccff","#40ff00","#ffc61a","#000099","#994d00","#006600","#6600cc","#ff9900","#8533ff","#4700b3","#9933ff","#669900","#009900","#ff00ff","#ff99ff","#ff0066","#ffffff","#666699","#996633"]

level_order_dict = {k:['High','Decent','Low'] for k in spotify.columns if '_level' in k}

order_dict={"artist_count":["1","2","3","4+"],
            "released_month":[1,2,3,4,5,6,7,8,9,10,11,12],
            "day_of_week":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "mode":["Major","Minor"],
            "month_name":["January","February","March","April","May","June","July","August","September","October","November","December"]}
order_dict.update(level_order_dict)


main_cols = ['track_name', 'artists_name', 'artist_count', 'released_year', 'in_spotify_playlists', 'in_spotify_charts', 'streams']
factors = ['danceability_percentage_value', 'valence_percentage_value', 'energy_percentage_value', 'acousticness_percentage_value', 
           'liveness_percentage_value', 'speechiness_percentage_value']
levels = ['danceability_level', 'valence_level', 'energy_level', 'acousticness_level', 'liveness_level', 'speechiness_level']
main_values = ['track_name', 'artists_name', 'streams']
playlists = ['in_spotify_playlists', 'in_apple_playlists', 'in_deezer_playlists']
levels_short = ['danceability_level', 'valence_level', 'energy_level']

num_cols = np.setdiff1d(spotify_graph.select_dtypes(include='number').columns, ["released_day"])
cat_cols = np.setdiff1d(spotify_graph.select_dtypes(include=['category','object']).columns,["track_name","artists_name","released_month"])

num_dict = {'acousticness_percentage_value':'Acousticness (%)',
            'artist_count_precise':'Number of Artists',
            'bpm':'BPM',
             'danceability_percentage_value':'Danceability (%)',
             'energy_percentage_value':'Energy (%)',
             'in_apple_charts':'Rank on Apple Music Charts',
             'in_apple_playlists':'Number of Apple Music Playlists',
             'in_deezer_charts':'Rank on Deezer Charts',
             'in_deezer_playlists':'Number of Deezer Playlists',
             'in_shazam_charts':'Rank on Shazam Charts',
             'in_spotify_charts':'Rank on Spotify Charts',
             'in_spotify_playlists':'Number of Spotify Playlists',
             'instrumentalness_percentage_value':'Instrumentalness (%)',
             'liveness_percentage_value':'Liveness (%)',
             'released_year':'Year of Song Release',
             'streams':'Number of Streams on Spotify',
             'speechiness_percentage_value':'Speechiness (%)',
             'valence_percentage_value':'Valence (%)'
             }


cat_dict = {'artist_count':'Number of Artists',
            'acousticness_level':'Level of Acousticness',
            'danceability_level':'Level of Danceability',
            'day_of_week':'Day of Release',
            'energy_level':'Level of Energy',
            'key':'Key of the Song',
            'liveness_level':'Level of Liveness',
            'mode':'Mode of the Song',
            'month_name':'Month of Release',
            'released_year_category':'Year of Release',
            'speechiness_level':'Level of Speechiness',
            'valence_level':'Level of Valence',
            'track_name':'Song Title',
            'artists_name':'Name of Artist(s)'}


percent_dict = {'danceability_percentage_value':'Danceability (%)',
                'energy_percentage_value':'Energy (%)',
                'acousticness_percentage_value':'Acousticness (%)',
                'instrumentalness_percentage_value':'Instrumentalness (%)',
                'liveness_percentage_value':'Liveness (%)',
                'speechiness_percentage_value':'Speechiness (%)',
                'valence_percentage_value':'Valence (%)'}

level_dict = {'energy_level':'Level of Energy',
              'danceability_level':'Level of Danceability',
              'liveness_level':'Level of Liveness',
              'speechiness_level':'Level of Speechiness',
              'valence_level':'Level of Valence',
              'acousticness_level':'Level of Acousticness'}

level_dict_short = {'energy_level':'Level of Energy',
              'danceability_level':'Level of Danceability',
              'valence_level':'Level of Valence'}

attribute_dict = {'mode':'Mode of the Song',
                  'key':'Key of the Song',
                  'energy_level':'Level of Energy',
                'danceability_level':'Level of Danceability',
                'liveness_level':'Level of Liveness',
                'speechiness_level':'Level of Speechiness',
                'valence_level':'Level of Valence',
                'acousticness_level':'Level of Acousticness'}

popularity_dict = {'streams':'Number of Streams on Spotify',
                             'in_spotify_playlists':'Number of Spotify Playlists',
                             'in_spotify_charts':'Rank on Spotify Charts',
                             'in_apple_playlists':'Number of Apple Music Playlists',
                             'in_apple_charts':'Rank on Apple Music Charts',
                             'in_deezer_playlists':'Number of Deezer Playlists',
                             'in_deezer_charts':'Rank on Deezer Charts',
                             'in_shazam_charts':'Rank on Shazam Charts'}

playlists_and_charts_dict = {'in_spotify_playlists':'Number of Spotify Playlists',
                             'in_spotify_charts':'Rank on Spotify Charts',
                             'in_apple_playlists':'Number of Apple Music Playlists',
                             'in_apple_charts':'Rank on Apple Music Charts',
                             'in_deezer_playlists':'Number of Deezer Playlists',
                             'in_deezer_charts':'Rank on Deezer Charts',
                             'in_shazam_charts':'Rank on Shazam Charts'}

playlists_dict = {'in_spotify_playlists':'Number of Spotify Playlists',
                  'in_apple_playlists':'Number of Apple Music Playlists',
                  'in_deezer_playlists':'Number of Deezer Playlists'}

time_dict = {'day_of_week':'Day of Release',
             'month_name':'Month of Release'}

all_cols_dict = num_dict.copy()
all_cols_dict.update(cat_dict)
all_cols_dict.update({'released_date':'Date of Release','factors':'Audio Feature','percentage':'Percentage'})


melt1 = spotify_graph.rename(columns=percent_dict).melt(id_vars=main_cols, value_vars=list(percent_dict.values()), var_name="factors", value_name="percentage")
melt2 = spotify_graph.rename(columns=level_dict).melt(id_vars=main_cols, value_vars=list(level_dict.values()), var_name="factors", value_name="level")
melt3 = spotify_graph.rename(columns=playlists_dict).melt(id_vars=main_values, value_vars=list(playlists_dict.values()), var_name="playlists", value_name="value")
melt4 = spotify_artists.rename(columns=level_dict).melt(id_vars=main_values, value_vars=list(level_dict_short.values()), var_name="factors", value_name="level")



with st.sidebar: 
	selected = option_menu(
		menu_title = 'Navigation Pane',
		options = ['Abstract', 'Background Information', 'Data Cleaning','Exploratory Analysis', 'Analysis of Song Features', 'Analysis of Playlists & Time Factors', 'Analysis of Artists', 'Conclusion', 'Bibliography'],
		menu_icon = 'music-note-list',
		icons = ['bookmark-check', 'book', 'box', 'map', 'file-earmark-music-fill', 'headphones', 'music-player-fill', 'bar-chart', 'check2-circle'],
		default_index = 0,
		)





if selected=='Abstract':
    st.title("Spotify Abstract")
    st.markdown("Nowadays, we all can listen to music through our mobile apps, such as Spotify, Apple Music, and many of us enjoy listen to songs that we like. However, have you ever wondered why many people would love certain songs, and why they are popular as it is today? What are the “scientific” factors that makes certain tracks more popular than others?")
    st.markdown("Based on a given dataset, we will come up with scientific reasons that would answer these questions through this case study! This case study aims to explore certain patterns in the dataset, to understand what scientifically make a track popular, the factors that make the tracks popular, and the user preferences of popular songs. Without further ado, let’s get started!")

    st.markdown("<i>This app is best viewed in light mode, click on settings and then select \"light\".</i>",unsafe_allow_html=True)




if selected=="Background Information":
    st.title("Background Information")
    
    st.markdown("Spotify, a Swedish audio streaming platform, is one of the largest music applications, as well as one of the most prominent music streaming service that we use today. As of September 2023, Spotify has over 100 million tracks, more than 574 million users, including 226 million subscribers.<sup>1</sup> Spotify generates “popular tracks” based on the number of all-time and recent streams.<sup>2</sup>",unsafe_allow_html=True)
    
    st.markdown("The Spotify dataset provides information of the most streamed songs on Spotify, as of 2023. The dataset contains the most popular songs released from 20th century up to 2023, by solo artists, duets, groups, or multi-artist collaborations. Each row in the dataset contains information on a specific song, including its name, artist(s), number of artists featured (artist count), released date, number of streams, presence in playlists and charts on platforms like Spotify, Apple Music, Deezer, as well as various audio features including danceability, valence, energy, etc., that are considered as the scientific attributes of a song.",unsafe_allow_html=True)
    st.markdown("Each of the audio features range from 0 to 100%, to describe how much of those attributes are present in the particular track. Danceability measures how much the track is suitable for dancing based on its musical elements (such as tempo, rhythm stability, beat strength, etc.); Valence describes the musical positiveness that the track conveys, that it measures how happy, cheerful, euphoric (if the track sounds positive), or how sad, depressed, angry (if the track sounds negative) a particular track is. Energy is a perceptual measure of intensity and activity, that more energy means that the track is fast, loud or noisy enough. Acousticness is a confidence measure of whether the track is acoustic. Instrumentalness measures how much the track is an “instrumental”, meaning that no spoken words are present. Liveness detects the audience presence in the recording, meaning an increased probability that the track was performed live. Speechiness detects the presence of spoken words in a track, and tracks like talk show, audio book, poetry usually comes close to 100% of speechiness.<sup>3</sup>",unsafe_allow_html=True)
    st.markdown("We will first look at the previous studies on Spotify's popular tracks by experts. According to previous studies on Spotify’s top tracks in 2019, not all danceable songs are popular, but tracks with a danceability ranging from 64-84% (higher level) are the most popular ones on Spotify. Meanwhile, tracks with a moderate amount of energy (43-65%) can be more popular than tracks with low energy (below 40%) or with very high energy (above 80%). Low levels of speechiness also makes the track more popular, as the audience usually want to listen to the lyrics of the song instead of spoken words. Acousticness within 1-59% is a good range, but sometimes people don’t like acousticness around 1-30%, meaning that acousticness also depends on the genre of the track. Valence, however, doesn’t have much effect on the popularity of the song. In fact, the song’s artist(s) can also make the song itself popular, especially for the most popular artists.<sup>4</sup>",unsafe_allow_html=True)
    st.markdown("From the top 10 most popular songs on Spotify during 2017, all songs have high levels of danceability (above 60%), they are low on liveness & speechiness, and they all have mid-to-high energy (40-80%). 9 out of 10 songs are very low on acousticness, with one exception being Ed Sheeran’s “Shape of You”. Valence, though, is quite spread out around the mid-to-high region. As for instrumentalness, most popular tracks seem to have a value that is near or equal to 0.<sup>3</sup>",unsafe_allow_html=True)
    st.markdown("According to a 2021 study on the same topic, popularity increases with higher danceability and energy scores and lower acousticness and instrumentalness scores. Not only that, but tracks written in keys of B, A and E have the highest average popularity score, while for the modes of the track (major, minor), there isn’t a large difference in average popularity. These claims will be tested in the case study, to examine the 2023 trends and explain more “scientifically” of what makes certain tracks more popular than others.<sup>5</sup>",unsafe_allow_html=True)
    st.markdown("Apart from creating users’ own playlists, Spotify is well-known for its algorithmic approach to recommend songs via playlists to users, based on their listening patterns, including personalized playlists like Discover Weekly, expertly curated playlists for certain genre(s), hand-picked playlists featuring the latest hits; Spotify also allows for collaborative playlists, where it allows for creating playlists with your friends and modify it together.<sup>6</sup> Meanwhile, Apple Music doesn’t support collaborative playlists, and doesn’t have Spotify’s algorithm-based approach, but it is still useful for curating playlists that appeal to users’ own preferences.<sup>7</sup>", unsafe_allow_html=True)
    st.markdown("Playlists are essential for success on the music streaming platforms, by collaborating with curators and pitching tracks for the relevant playlists, artists can gain much more streams and greater exposure.<sup>8</sup> This case study also aims to discuss the patterns of streams on Spotify, versus the number of playlists on each of those platforms.", unsafe_allow_html=True)




if selected=="Data Cleaning":
    st.title('Data Cleaning')
    st.markdown("The data cleaning process mainly involves replacing the special characters that appear when reading in the dataset, converting released days & months, adding a variable to measure the level of each musical attribute, and to melt the dataframe by certain variables to investigate, for graphing purposes.")
    
    st.markdown("Because of the special characters that appear in the track names and artist names, the encoding needs to be specified when reading in the data:")
    code_insert='''file_path = '/Users/mac/Desktop/files/Data_Science_Python'\nspotify=pd.read_csv(file_path+'/spotify.csv', encoding='latin-1')'''
    st.code(code_insert,language='python')
    
    st.markdown("Some of the characters were read in as Unicode hexadecimal characters, so I had to replace it with the original characters in the track name and artist name. For example, the 'ñ' character was read in as \ x96 ('\x96'), so I had to replace the original character back to its place:")
    replacing_code = '''spotify['artists_name']=spotify['artists_name'].str.replace("\x96","ñ")'''
    st.code(replacing_code,language='python')
    
    st.markdown("The analysis requires a precise day-of-week variable (Monday to Sudnay) and a month name variable (January to December). Hence, the original released_year, released_month, released_day columns are combined together as a datetime variable, for extracting the converted day of week and month names, and to make it as new columns of the Spotify dataframe.")
    datetime_code = '''date_cols = spotify[['released_year','released_month','released_day']]
spotify['released_date'] = pd.to_datetime(date_cols.rename(columns={'released_year':'year', 'released_month':'month', 'released_day':'day'}))
spotify['day_of_week'] = spotify['released_date'].dt.day_name()
spotify['month_name'] = spotify['released_date'].dt.month_name()'''
    st.code(datetime_code,language='python')
    
    st.markdown("Each of the musical features (danceability, valence, energy, etc. in %) needs to be converted to a level variable and assigned to a column. Based on the experts' studies on those musical attributes, I have set the 'High' level to above or equal to 65%, 'Decent' level to 40%-64%, and 'Low' level to below 40%. I have defined a function in order to do this:")
    func_code = '''def label(element):
        if element >= 65:
            return 'High'
        elif element >= 40:
            return 'Decent'
        else:
            return 'Low' '''
    st.code(func_code,language='python')
    
    st.markdown("Then the function is applied on each of the musical attribute columns (in %), to create new columns for each. For example, the following line shows that the function is applied on the danceability column:")
    apply_code = '''spotify['danceability_level'] = spotify['danceability_percentage_value'].map(label)'''
    st.code(apply_code,language='python')
    
    st.markdown("The case study will focus on analyzing the musical attribute variables and the artist variable. To make graphs based on those different variables, melts of the original Spotify dataframe should be created. For example, the following code melts the dataframe by the musical attribute percentage variables, and is assigned to melt1:")
    melt_code = '''melt1 = spotify.rename(columns=percent_dict).melt(id_vars=main_cols,
                                                  value_vars=list(percent_dict.values()), 
                                                  var_name="factors",
                                                  value_name="percentage")'''
    st.code(melt_code,language='python')
    
    st.markdown("Now, we will take a look at the cleaned dataset that's ready for analysis:")
    st.dataframe(spotify.head(10))




if selected=="Exploratory Analysis":
    st.title('Exploratory Analysis')
    
    st.header("Exploring by Musical Attributes")
    st.markdown("The following graphs will explore mainly on the song features, including danceability, valence, energy, acousticness, instrumentalness, liveness, speechiness, as well as the Key and Mode of the tracks, versus the number of streams they receive on spotify.")
    
    st.subheader("Histogram: Average number of Streams vs. Musical Attributes of Tracks")
    
    col13,col14=st.columns([3,5])
    col13.markdown("For this histogram, select one numeric and one category column to see the relationship of average streams on Spotify versus other song attributes")
    
    with st.form("Histogram with two numeric variables: Streams vs. other variables"):
        x_select_new = col13.selectbox("select a variable for the x-axis", percent_dict.values(),key=180)
        x_select = [k for k,v in percent_dict.items() if v == x_select_new][0]
        color_select_new = col13.selectbox("select a variable for the color labels", attribute_dict.values(),key=190)
        color_select = [k for k,v in attribute_dict.items() if v == color_select_new][0]
        col13_checkbox = col13.checkbox("Check to specify the number of bins",key=220)
        submitted=st.form_submit_button("Submit to produce the histogram")
        bins = 10
        if col13_checkbox:
            col13_number_input = col13.number_input("Enter a number to specify the number of bins", min_value=5, placeholder="Type a number...")
            bins = col13_number_input
        if submitted:
            fig = px.histogram(spotify_graph, x=x_select, y="streams", color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, barmode="group", histfunc="avg", nbins=bins, title=f"Average number of Streams vs. {x_select_new}")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text=f"<b>{x_select_new}</b>", title_font_size=16)
            fig.update_yaxes(title_text="<b>Average of Streams on Spotify</b>", title_font_size=16)
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            col14.plotly_chart(fig)
    
    
    st.subheader("Bar Chart: Streams vs. Musical Attributes of Tracks")
    
    col19,col20=st.columns([3,5])
    col19.markdown("Select one category column representing the level of a musical attribute, to see the relationship of streams on Spotify versus different categories of each song attribute")
    
    with st.form("Histogram: Streams vs. musical attributes"):
       color_select_new = col19.selectbox("Select one category variable for the color groups", attribute_dict.values(), key=505)
       color_select = [k for k,v in attribute_dict.items() if v == color_select_new][0]
       col19_checkbox = col19.checkbox("Check for a normalized bar chart",key=440)
       submitted=st.form_submit_button("Submit to produce bar chart")
       if submitted:
           percent = None
           percent_str = "Count"
           total = "Total"
           if col19_checkbox:
               percent = "percent"
               percent_str = "Percent (%)"
               total = "Percent (%) of"
           fig_2 = px.histogram(spotify_graph, x="streams", color=color_select, facet_col=color_select, facet_col_wrap=2, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, histnorm=percent, facet_row_spacing=0.1, height=800, title=f"Streams vs. {color_select_new}")
           fig_2.update_traces(marker_line_width=1)
           fig_2.update_yaxes(title_text=f"<b>{percent_str}</b>", title_font_size=14)
           fig_2.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
           fig_2.update_layout(xaxis=dict(title_text="<b>Number of Streams</b>"),
                               xaxis2=dict(title_text="<b>Number of Streams</b>"))
           fig_2.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
           col20.plotly_chart(fig_2)
    
    
    
    st.subheader("Scatterplot: Streams vs. Different Musical Attributes")
    
    col17,col18=st.columns([3,5])
    col17.markdown("For the scatterplot, select one numeric column and one color column representing an audio feature of the tracks, to see the relationship of streams on Spotify versus audio features.")
    
    with st.form("Scatterplot with one numeric and one category variable"):
        y_select_new = col17.selectbox("select another numeric label for the y-axis",percent_dict.values(),key=80)
        y_select = [k for k,v in percent_dict.items() if v == y_select_new][0]
        color_select_new = col17.selectbox("Select one category variable for the color groups", level_dict.values(), key=90)
        color_select = [k for k,v in level_dict.items() if v == color_select_new][0]
        submitted=st.form_submit_button("Submit to produce the scatterplot")
        if submitted:
            fig = px.scatter(spotify_graph, x="streams", y=y_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=['track_name','artists_name'],title=f"Streams vs. {y_select_new}")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=16)
            fig.update_yaxes(title_text=f"<b>{y_select_new}</b>", title_font_size=16)
            fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            col18.plotly_chart(fig)
    
    
    st.subheader("Box Plot: Streams vs. Musical Attributes of Tracks")
    
    col21,col22=st.columns([3,5])
    col21.markdown("For the box plot, select one musical attribute variable (versus number of Streams on Spotify)")
    
    with st.form("Box plot with one musical attribute variable"):
        x_select_new = col21.selectbox("Select one category variable for the x-axis",attribute_dict.values(),key=150)
        x_select = [k for k,v in attribute_dict.items() if v == x_select_new][0]
        submitted=st.form_submit_button("Submit to produce the box plot")
        if submitted:
            fig = px.box(spotify_graph, x=x_select, y="streams", color=x_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"],title=f"{x_select_new} vs. Streams on Spotify")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text=f"<b>{x_select_new}</b>", title_font_size=14)
            fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col22.plotly_chart(fig)
    
    
    
    st.subheader("Box Plot: Popularity Factors vs. Musical Features")
    
    col25,col26=st.columns([3,5])
    col25.markdown("For the pie chart, select one musical attribute variable and one popularity factor variable")
    
    with st.form("Pie chart with one musical attribute variable and one popularity factor variable"):
        value_select_new = col25.selectbox("Select one popularity factor variable for the value",popularity_dict.values(),key=130)
        value_select = [k for k,v in popularity_dict.items() if v == value_select_new][0]
        name_select_new = col25.selectbox("select one musical attribute variable for the names",attribute_dict.values(),key=131)
        name_select = [k for k,v in attribute_dict.items() if v == name_select_new][0]
        submitted=st.form_submit_button("Submit to produce the pie chart")
        if submitted:
            fig = px.pie(spotify_graph, values=value_select, names=name_select, color=name_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict,title=f"{value_select_new} vs. {name_select_new}")
            fig.update_traces(marker_line_width=1)
            fig.update_traces(textposition='inside', textinfo='percent+label+text+value', texttemplate="<b>%{label}<br>%{value:.5s}<br>%{percent}</b>")
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            col26.plotly_chart(fig)
    
    
    
    
    
    st.header("Exploring by Playlists & Charts")
    st.markdown("The following graph explores the pattern between the tracks' streams on Spotify, with the number of playlists and their rank on Charts in platforms including Spotify, Apple Music, Deezer, and Shazam.")
    
    st.subheader("Scatterplot: Streams versus Total Number of Playlists & Rank on Charts")
    
    col15,col16=st.columns([3,5])
    col15.markdown("For the scatterplot, select one numeric column representing the total number of playlists that each track is in, or the rank of each track on different charts, to see the relationship of streams on Spotify versus playlists & rank.")
    
    with st.form("Scatterplot with two numeric variables"):
        y_select_new = col15.selectbox("select one popularity factor variable for the y-axis",playlists_and_charts_dict.values(),key=44)
        y_select = [k for k,v in playlists_and_charts_dict.items() if v == y_select_new][0]
        submitted=st.form_submit_button("Submit to produce the scatterplot")
        if submitted:
            fig = px.scatter(spotify_graph, x="streams", y=y_select,  category_orders=order_dict, labels=all_cols_dict, hover_data=['track_name','artists_name'],title=f"Streams vs. {y_select_new}")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=16)
            fig.update_yaxes(title_text=f"<b>{y_select_new}</b>", title_font_size=16)
            fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            col16.plotly_chart(fig)
    
    
    
    
    st.header("Exploring by Days & Months of Release")
    st.markdown("The following graph depicts the Streams on Spotify during different days of release (Monday to Sunday), as well as months of release (January to December) of each year.")
    
    st.subheader("Box Plot: Streams vs. Day & Month of Release")
    
    col23,col24=st.columns([3,5])
    col23.markdown("For the box plot, select one time variable and a popularity factor variable")
    
    with st.form("Box plot with one time variable and one popularity factor variable"):
        x_select_new = col23.selectbox("Select one time variable for the x-axis",time_dict.values(),key=160)
        x_select = [k for k,v in time_dict.items() if v == x_select_new][0]
        y_select_new = col23.selectbox("Select one popularity factor variable for the y-axis",popularity_dict.values(),key=162)
        y_select = [k for k,v in popularity_dict.items() if v == y_select_new][0]
        submitted=st.form_submit_button("Submit to produce the box plot")
        if submitted:
            fig = px.box(spotify_graph, x=x_select, y=y_select, color=x_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"],title=f"{x_select_new} vs. {y_select_new}")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text=f"<b>{x_select_new}</b>", title_font_size=14)
            fig.update_yaxes(title_text=f"<b>{y_select_new}</b>", title_font_size=14)
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col24.plotly_chart(fig)
    
    
    
    
    
    st.header("High Versus Low levels of Streams")
    st.markdown("For the following graphs, input a cutoff value to divide the level of Streams in High & Low values, and select one musical attribute variable to generate the graphs.")
    
    col27,col28=st.columns([3,5])
    col27.subheader("Pie chart: High vs. Low levels of Streams")
    
    with st.form("Pie chart with one musical attribute variable"):
        x_select_new = col27.selectbox("Select one category variable for the x-axis",attribute_dict.values(),key=1500)
        x_select = [k for k,v in attribute_dict.items() if v == x_select_new][0]
        
        col27_number_input = col27.number_input("Enter a number to specify the cutoff value between High and Low Value of Streams, e.g., 100 million (100000000)", min_value=50000000, placeholder="E.g., 100 million (100000000)", key=2200)
        cutoff_value = col27_number_input

        def label_streams(element):
            if element >= cutoff_value:
                return 'High Streams'
            else:
                return 'Low Streams'
        
        spotify_copy = spotify_graph.copy()
        spotify_copy['streams_level'] = spotify_copy['streams'].map(label_streams)
        
        submitted=st.form_submit_button("Submit to produce the pie chart")
        if submitted:
            fig = px.pie(spotify_copy, names=x_select, values="streams", color=x_select, color_discrete_sequence=color_list, facet_row ="streams_level", category_orders=order_dict, labels=all_cols_dict, height=800,  hover_data=["track_name","artists_name"],title=f"{x_select_new} vs. Streams on Spotify")
            fig.update_traces(marker_line_width=1)
            fig.update_traces(textposition='inside', textinfo='percent+label+text+value', texttemplate="<b>%{label}<br>%{value:.5s}<br>%{percent}</b>")
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col28.plotly_chart(fig)
    
    
    col29,col30=st.columns([3,5])
    col29.subheader("Box plot: High vs. Low levels of Streams")
    
    with st.form("Facet box plot with one musical attribute percentage ariable"):
        y_select_new = col29.selectbox("Select one numeric variable for the x-axis",percent_dict.values(),key=1600)
        y_select = [k for k,v in percent_dict.items() if v == y_select_new][0]
        
        col29_number_input = col29.number_input("Enter a number to specify the cutoff value between High and Low Value of Streams, e.g., 100 million (100000000)", min_value=50000000, placeholder="E.g., 100 million (100000000)", key=2400)
        cutoff_value = col29_number_input

        def label_streams(element):
            if element >= cutoff_value:
                return 'High Streams'
            else:
                return 'Low Streams'
        
        spotify_copy = spotify_graph.copy()
        spotify_copy['streams_level'] = spotify_copy['streams'].map(label_streams)
        
        submitted=st.form_submit_button("Submit to produce the box plot")
        if submitted:
            fig = px.box(spotify_copy, x='streams_level', y=y_select, color='streams_level', color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, height=800,  hover_data=["track_name","artists_name"],title=f"{y_select_new} vs. Level of Streams")
            fig.update_traces(marker_line_width=1)
            fig.update_xaxes(title_text="<b>Level of Streams</b>", title_font_size=14)
            fig.update_yaxes(title_text=f"<b>{y_select_new}</b>", title_font_size=14)
            fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col30.plotly_chart(fig)
    
    
    
    
    st.header("Exploring by Artists")
    st.markdown("The following graphs are used to explore the popular artists by number of streams of their tracks. By selecting certain artists, the graph will automatically add the artists' information to the graph.")
    
    st.subheader("Scatterplot: Streams vs. Music Attributes by Artist")
    st.markdown("The following scatterplot is for exploring the different artists' musical attributes by the avg number of streams, between solo releases and collaborations.")
    
    def label_artist(element):
        if element > 1:
            return 'Collaboration'
        else:
            return 'Solo'

    spotify['artist_type'] = spotify['artist_count_precise'].apply(label_artist)
    
    col31,col32=st.columns([3,5])
    
    with st.form("Scatterplot by artist"):
        x_select_new = col31.selectbox("Select one music attribute percentage variable for the y-axis",percent_dict.values(),key=1440)
        x_select = [k for k,v in percent_dict.items() if v == x_select_new][0]
        color_select_new = col31.multiselect('Select up to 10 artists', top_artists_list, key=1540, max_selections=10, default=top_artists_list[:2])
        color_select = [k for k in top_artists_list if k in color_select_new]
        filtered = spotify_artists[spotify_artists["artists_name"].isin(color_select)]
        submitted=st.form_submit_button("Submit to produce the scatterplot")
        if submitted:
            fig = px.scatter(filtered, y="streams", x=x_select, color="artists_name", color_discrete_sequence=color_list, facet_row="artist_type", category_orders=order_dict, labels=all_cols_dict, hover_data='track_name', title=f"Streams vs. {y_select_new} by artist", height=800)
            fig.update_traces(marker_line_width=1)
            fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=16)
            fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Artist Names</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.update_layout(xaxis=dict(title_text=f"<b>{x_select_new}</b>"))
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col32.plotly_chart(fig)
    
    
    st.subheader("Histogram: Streams vs. Music Attributes by Artist")
    st.markdown("The following histogram is for exploring the different artists' musical attributes by the avg number of streams, while it allows for comparison between solo releases and collaborations.")
    
    col33,col34,col35=st.columns([3,5,5])
    
    with st.form("Histogram by artist"):
        x_select_new = col33.selectbox("Select one music attribute variable for the x variables",percent_dict.values(),key=1445)
        x_select = [k for k,v in percent_dict.items() if v == x_select_new][0]
        color_select_new = col33.multiselect('Select up to 5 artists', top_artists_list, key=1545, max_selections=5, default=top_artists_list[:2])
        color_select = [k for k in top_artists_list if k in color_select_new]
        filtered = spotify_artists[spotify_artists["artists_name"].isin(color_select)]
        col33_checkbox_1 = col33.checkbox("Check to specify the number of bins",key=240)
        submitted=st.form_submit_button("Submit to produce the histogram")
        col33_checkbox_2 = col33.checkbox("Check to see the difference between Solo and Collaboration tracks",key=241)
        bins = 10
        if col33_checkbox_1:
            col33_number_input = col33.number_input("Enter a number to specify the number of bins", min_value=0, placeholder="Type a number...")
            bins = col33_number_input
        if submitted:
            facet = None
            if col33_checkbox_2:
                facet = "artist_type"
            fig = px.histogram(filtered, x=x_select, y="streams", color="artists_name", facet_row=facet, color_discrete_sequence=color_list, category_orders=order_dict, barmode="group", histfunc="avg", labels=all_cols_dict, hover_data='track_name', title=f" {x_select_new} vs. Streams", width=800, height=800, nbins=bins)
            fig.update_traces(marker_line_width=1)
            fig.update_yaxes(title_text="<b>Average of Streams</b>")
            fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Artist Names</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.update_layout(xaxis=dict(title_text=f"<b>{x_select_new}</b>"))
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col34.plotly_chart(fig)
    
    
    st.subheader("Histogram: Number of tracks vs. Music Attributes by Artist")
    st.markdown("The following histogram is for exploring the number of tracks by different artists present in the dataset versus their musical attributes.")
    col36,col37,col38=st.columns([3,5,5])
    
    with st.form("Histogram by artist 2"):
        x_select_new = col36.selectbox("Select one music attribute variable for the x variables",percent_dict.values(),key=1448)
        x_select = [k for k,v in percent_dict.items() if v == x_select_new][0]
        color_select_new = col36.multiselect('Select up to 5 artists', top_artists_list, key=1501, max_selections=5, default=top_artists_list[:2])
        color_select = [k for k in top_artists_list if k in color_select_new]
        filtered = spotify_artists[spotify_artists["artists_name"].isin(color_select)]
        col36_checkbox = col36.checkbox("Check to specify the number of bins",key=244)
        col36_checkbox_2 = col36.checkbox("Check to see the difference between Solo and Collaboration tracks",key=245)
        submitted=st.form_submit_button("Submit to produce the histogram")
        bins = 10
        if col36_checkbox:
            col36_number_input = col36.number_input("Enter a number to specify the number of bins", min_value=0, placeholder="Type a number...", key=362)
            bins = col36_number_input
        if submitted:
            facet = None
            if col36_checkbox_2:
                facet = "artist_type"
            fig = px.histogram(filtered, x=x_select, color="artists_name", facet_row=facet, color_discrete_sequence=color_list, category_orders=order_dict, barmode="group", labels=all_cols_dict, hover_data='track_name', title=f"Number of Tracks By {x_select_new}", width=800, height=800, nbins=bins)
            fig.update_traces(marker_line_width=1)
            fig.update_yaxes(title_text="<b>Number of Tracks</b>")
            fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Artist Names</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
            fig.update_layout(xaxis=dict(title_text=f"<b>{x_select_new}</b>"))
            fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
            col37.plotly_chart(fig)
    
    
    
    
    st.subheader("Box plot: Streams vs. Music Attributes by Artist")
    st.markdown("The following box plot, again, is for exploring the different artists' musical attributes versus the avg number of streams, but we will look at solo and collaborations all together in this graph.")
    
    col36,col37,col38=st.columns([3,5,5])
    
    with st.form("Box plot by artist"):
        color_select_new = col36.selectbox("Select one category variable for the colors",level_dict.values(),key=155)
        color_select = [k for k,v in level_dict.items() if v == color_select_new][0]
        x_select_new = col36.multiselect('Select up to 5 artists', top_artists_list, key=1548, max_selections=5, default=top_artists_list[:2])
        x_select = [k for k in top_artists_list if k in x_select_new]
        filtered = spotify_artists[spotify_artists["artists_name"].isin(x_select)]
        fig = px.box(filtered, x="artists_name", y="streams", color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title=f"{color_select_new} vs. Streams on Spotify", height=500, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_xaxes(title_text="<b>Name of Artists</b>", title_font_size=14)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text=f"<b>{color_select_new}</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        col37.plotly_chart(fig)
    
    
    
    
    col1,col2=st.columns([3,5])
    col1.markdown("Select two numeric columns and one category column")
    
    with st.form("Histogram with two numeric variables"):
        x_select_new = col1.selectbox("Select one numeric label for the x-axis",num_dict.values(),key=1)
        x_select = [k for k,v in num_dict.items() if v == x_select_new][0]
        y_select_new = col1.selectbox("select a different numeric label for the y-axis",np.setdiff1d(list(num_dict.values()),x_select),key=2)
        y_select = [k for k,v in num_dict.items() if v == y_select_new][0]
        color_select_new = col1.selectbox("Select one category variable for the color groups", cat_dict.values(), key=3)
        color_select = [k for k,v in cat_dict.items() if v == color_select_new][0]
        col1_checkbox = col1.checkbox("Check to specify the number of bins",key=30)
        submitted=st.form_submit_button("Submit to produce the histogram")
        bins = None
        if col1_checkbox:
            col1_number_input = col1.number_input("Enter a number to specify the number of bins", min_value=0, placeholder="Type a number...")
            bins = col1_number_input
        if submitted:
            fig = px.histogram(spotify_graph, x=x_select, y=y_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, barmode="group", histfunc="avg", nbins=bins)
            fig.update_traces(marker_line_width=1)
            col2.plotly_chart(fig)
    
    
    
    
    col3,col4=st.columns([3,5])
    col3.markdown("Select two category columns and one numeric column")
    
    with st.form("Bar chart with two category variables and one numeric variable"):
        x_select_new = col3.selectbox("Select one numeric label for the x-axis",num_dict.values(),key=4)
        x_select = [k for k,v in num_dict.items() if v == x_select_new][0]
        y_select_new = col3.selectbox("select one category label for the y-axis",cat_dict.values(),key=5)
        y_select = [k for k,v in cat_dict.items() if v == y_select_new][0]
        color_select_new = col3.selectbox("Select another category variable for the color groups", np.setdiff1d(list(cat_dict.values()),y_select), key=6)
        color_select = [k for k,v in cat_dict.items() if v == color_select_new][0]
        col3_checkbox = col3.checkbox("Check for a normalized bar chart",key=500)
        submitted=st.form_submit_button("Submit to produce the histogram")
        if submitted:
            percent = None
            if col3_checkbox:
                percent = "percent"
                avg = None
            else:
                avg = "avg"
            fig = px.histogram(spotify_graph, x=x_select, y=y_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, barmode="group", histnorm=percent, histfunc=avg)
            fig.update_yaxes(type="category")
            fig.update_traces(marker_line_width=1)
            col4.plotly_chart(fig)
    
    
    col11,col12=st.columns([3,5])
    col11.markdown("Select two category columns for the bar chart")
    
    with st.form("Bar chart with two category variables"):
        
        x_select_new = col11.selectbox("select one category variable for the x-axis",cat_dict.values(),key=16)
        x_select = [k for k,v in cat_dict.items() if v == x_select_new][0]
        color_select_new = col11.selectbox("Select another category variable for the color groups", np.setdiff1d(list(cat_dict.values()),x_select), key=17)
        color_select = [k for k,v in cat_dict.items() if v == color_select_new][0]
        col11_checkbox = col11.checkbox("Check for a normalized bar chart",key=1000)
        submitted=st.form_submit_button("Submit to produce bar chart")
        if submitted:
            percent = None
            if col11_checkbox:
                percent = "percent"
            fig_2 = px.histogram(spotify_graph, x=x_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, barmode="group", histnorm=percent)
            fig_2.update_xaxes(type="category")
            fig_2.update_traces(marker_line_width=1)
            col12.plotly_chart(fig_2)
    
    
    
    col5,col6=st.columns([3,5])
    col5.markdown("For the scatterplot, select two numeric columns and one category column")
    
    with st.form("Scatterplot with two numeric variables and one category variable"):
        x_select_new = col5.selectbox("Select one numeric label for the x-axis",num_dict.values(),key=7)
        x_select = [k for k,v in num_dict.items() if v == x_select_new][0]
        y_select_new = col5.selectbox("select another numeric label for the y-axis",np.setdiff1d(list(num_dict.values()),x_select),key=8)
        y_select = [k for k,v in num_dict.items() if v == y_select_new][0]
        color_select_new = col5.selectbox("Select one category variable for the color groups", cat_dict.values(), key=9)
        color_select = [k for k,v in cat_dict.items() if v == color_select_new][0]
        submitted=st.form_submit_button("Submit to produce the scatterplot")
        if submitted:
            fig = px.scatter(spotify_graph, x=x_select, y=y_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=['track_name','artists_name'])
            fig.update_traces(marker_line_width=1)
            col6.plotly_chart(fig)
    
    
    
    col7,col8=st.columns([3,5])
    col7.markdown("For the box plot, select two numeric columns and one category column")
    
    with st.form("Box plot with two numeric variables and one category variable"):
        x_select_new = col7.selectbox("Select one category variable for the x-axis",cat_dict.values(),key=10)
        x_select = [k for k,v in cat_dict.items() if v == x_select_new][0]
        y_select_new = col7.selectbox("select one numeric label for the y-axis",num_dict.values(),key=11)
        y_select = [k for k,v in num_dict.items() if v == y_select_new][0]
        color_select_new = col7.selectbox("Select a different category variable for the color groups", np.setdiff1d(list(cat_dict.values()),x_select), key=12)
        color_select = [k for k,v in cat_dict.items() if v == color_select_new][0]
        submitted=st.form_submit_button("Submit to produce the box plot")
        if submitted:
            fig = px.box(spotify_graph, x=x_select, y=y_select, color=color_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict)
            fig.update_traces(marker_line_width=1)
            col8.plotly_chart(fig)
    
    
    
    col9,col10=st.columns([3,5])
    col9.markdown("For the pie chart, select two numeric columns and one category column")
    
    with st.form("Pie charts with two category variables and one numeric variable"):
        value_select_new = col9.selectbox("Select one numeric label for the value",num_dict.values(),key=13)
        value_select = [k for k,v in num_dict.items() if v == value_select_new][0]
        name_select_new = col9.selectbox("select one category variable for the names",cat_dict.values(),key=14)
        name_select = [k for k,v in cat_dict.items() if v == name_select_new][0]
        submitted=st.form_submit_button("Submit to produce the pie chart")
        if submitted:
            fig = px.pie(spotify_graph, values=value_select, names=name_select, color=name_select, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict)
            fig.update_traces(marker_line_width=1)
            fig.update_traces(textposition='inside', textinfo='percent+label+text+value', texttemplate="%{label}<br>%{value:.5s}<br>%{percent}")
            col10.plotly_chart(fig)
            col10.write(fig.data[0])








if selected=="Analysis of Song Features":
    st.title("Analysis of Song Features")
    st.header("Comparing different Spotify audio features")
    st.markdown("First, let's look at some of Spotify's audio features (danceability, valence, energy, acousticness, liveness, speechiness) and how it influences the streams of the tracks.")
    st.subheader("Streams on Spotify vs. Audio features")
    
    col1,col2,col2_new=st.columns([4,5,5])
    with st.form("Histogram: Streams vs. musical attributes 1"):
       fig_1 = px.histogram(melt2, x="streams", color="level", facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.1, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, log_y=True, barmode="group", title="Streams vs. Level of Musical Attributes", height=800, nbins=10)
       fig_1.update_traces(marker_line_width=1)
       fig_1.update_yaxes(title_text="<b>Count</b>", title_font_size=14)
       fig_1.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
       fig_1.update_layout(xaxis=dict(title_text="<b>Number of Streams</b>"),
                           xaxis2=dict(title_text="<b>Number of Streams</b>"))
       fig_1.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=13))
       
       col2.plotly_chart(fig_1)
       
       col1.markdown(" ")
       col1.markdown(" ")
       col1.markdown("There are more counts of popular tracks with high levels of danceability than decent or low levels. Although the Danceability and Energy graphs follow a similar pattern, there are more most-streamed tracks with high energy, while the two tracks with highest streams have high and decent danceability altogether. Also, there are more tracks with 2.5B-3B streams (which is also a relatively high range of streams) in Decent energy level than High.")
       
    
       col1.markdown(" ")
       col1.markdown("For Valence, however, there is overall not much difference between the three graphs, except there is more songs with Decent valence that are more streamed (above 2B), while the two most streamed songs have a High and Low level of valence respectively. The levels of Valence are spread out within the higher range of streams.")
       col1.markdown("Tracks with Low levels of Acousticness, Liveness and Speechiness are generally more streamed on Spotify, while there are also some most-streamed tracks with Decent and High levels of Acousticness.")
       col1.markdown(" ")
       col1.markdown(" ")
       col1.markdown(" ")
       col1.markdown(" ")
    
    
    col12,col13,col14=st.columns([4,5,5])
    
    with st.form("Scatterplot: Streams vs. musical attributes"):
       fig_2 = px.scatter(melt1, x="streams", y="percentage", color="factors", facet_col="factors", facet_col_wrap=2, color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=['track_name','artists_name'], height=900, width=800, title="Streams vs. Musical Attributes")
       fig_2.update_traces(marker_line_width=0.7)
       fig_2.update_yaxes(title_text="<b>Percentage (%)</b>", title_font_size=14)
       fig_2.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Musical Attribute</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
       fig_2.update_layout(xaxis=dict(title_text="<b>Number of Streams</b>"),
                           xaxis2=dict(title_text="<b>Number of Streams</b>"),
                           legend=dict(x=0.8,y=0.22,xanchor='right',yanchor='top'))
       fig_2.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=13))
       
       col13.plotly_chart(fig_2)
       col12.markdown("The scatterplots show each of the different audio attribute percentages versus the number of streams.")
       col12.markdown("There is no clear differences in pattern on the scatterplots of Danceability, Valence and Energy percentages, as its percentage values are spread out from low to high levels. However, we can see that the data points on Danceability and Energy are more concentrated in mid-to-high levels. This means that tracks with medium to high levels of Danceability and Energy are the more popular ones, yet Valence doesn't really have an influence on the tracks' popularity.")
       col12.markdown("In the scatter plot, Acousticness value is also pretty spread out, but many tracks with mid-to-high Acousticness values does not go beyond 2B streams. Most of the popular tracks are concentrated at mid-to-low values of Liveness and Speechiness, while for Instrumentalness, vast majority of the tracks are in 0%.")
       col12.markdown(" ")
       col12.markdown(" ")
    
    
    
    col15,col16,col_17=st.columns([4,5,5])
    
    fig = px.pie(melt2, values="streams", names="level", color="level", facet_col="factors", facet_col_wrap=2, color_discrete_map={"High": "#ff0000", "Decent": "#663300", "Low": "#00ffff"}, category_orders=order_dict, labels=all_cols_dict, title="Streams vs. Musical Attributes", height=800, width=800)
    fig.update_traces(marker_line_width=1)
    fig.update_traces(textposition='inside', textinfo='percent+label+text+value', texttemplate="<b>%{label}<br>%{value:.5s}<br>%{percent}</b>")
    fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
    fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=13))
        
    col16.plotly_chart(fig)
    col15.markdown("")
    col15.markdown("")
    col15.markdown("(Note: G stands for Giga, corresponding to 10^9, equivalent to Billions.)")
    col15.markdown("The pie chart shows clearly of which level of certain musical attributes receive the greatest number of Streams on Spotify.")
    col15.markdown("We can clearly see that among all popular songs on Spotify, high levels of Energy and Danceability, as well as low levels of Acousticness, Liveness and Speechiness, have the greatest Streams on Spotify in total.")
    col15.markdown("Meanwhile, decent levels of Danceability and Energy also take up  fair amount of percentages on the graph. As for Valence, although Decent levels cover the most percentage, overall the three levels doesn't have much difference with each other, meaning that tracks, regardless of High, Decent or Low Valence, may all receive greater streams on Spotify.")
        
    st.markdown("From the above observations, we found that tracks with mid-to-high levels of Danceability and Energy, low levels of acousticness, liveness and speechiness, near or equal to 0% of Instrumentalness, are all likely to be more popular on Spotify, as expected. Valence also doesn't have much effect on the popularity of a track. However, more popular tracks can also have mid-to-high levels of Acousticness.")
    
    
    
    
    st.subheader("Streams on Spotify versus Mode and Key of the tracks")
    st.markdown("Now we will look at the Mode of the tracks (Major, Minor) and the Key of each track that are the most popular ones.")
    
    col3,col4,col5=st.columns([4,4,5])
       
    with st.form("Box plot: Streams vs. Mode"):
        fig = px.box(spotify_graph, x="mode", y="streams", color="mode", color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"], height=600, title="Mode of the Song vs. Streams on Spotify")
        fig.update_traces(marker_line_width=1)
        fig.update_xaxes(title_text="<b>Mode</b>", title_font_size=14)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.25, legend_title_font_size=14, legend_title_text="<b>Mode</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col4.plotly_chart(fig)
        col3.markdown("")
        col3.markdown("")
        col3.markdown("The box plot shows a clear comparison between the variables and their number of Streams. Between Major and Minor keys, by looking at the median, upper fence and the maximum point of the graphs, there is a clear difference that tracks in Major keys received more streams than Minor keys.")
    
    
    col3_new,col4_new,col5_new=st.columns([4,4,5])
       
    with st.form("Box plot: Streams vs. Key"):
        fig = px.box(spotify_graph, x="key", y="streams", color="key", color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"], height=600, title="Key of the Song vs. Streams on Spotify")
        fig.update_traces(marker_line_width=1)
        fig.update_xaxes(title_text="<b>Key</b>", title_font_size=14)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.3, legend_title_font_size=14, legend_title_text="<b>Key</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col4_new.plotly_chart(fig)
        col3_new.markdown("")
        col3_new.markdown("")
        col3_new.markdown("")
        col3_new.markdown("In this dataset, however, tracks written in the key of C# have the greatest number of streams, followed by tracks in D and F#. Meanwhile, the hypothesized keys of B, A and E actually have mid-to-low numbers of streams, by looking at each of their medians, upper fences, and max values.")
    
    
    
    
if selected == "Analysis of Playlists & Time Factors":
    st.title("Analysis of Playlists & Time Factors")
    st.header("Comparing different factors that may affect Streams")
    st.markdown("Now, we will look at the relationship between the number of playlists on music streaming templates with Streams on Spotify, as well as the time factors including day of release (Monday to Sunday) and month of release (January to December) per each year.")
    st.subheader("Comparing Number of Playlists with Streams")
    
    col6,col7,col8=st.columns([4,4,5])
    
    with st.form("Scatterplot with two numeric variables"):
        fig = px.scatter(melt3, x="streams", y="value", color="playlists", facet_col="playlists", facet_col_wrap=2, facet_row_spacing=0.1, category_orders=order_dict, labels=all_cols_dict, hover_data=['track_name','artists_name'],title="Streams vs. Playlists", height=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="Number of Playlists</b>", title_font_size=16, matches=None)
        fig.update_layout(title_x=0.4, legend_title_font_size=14, legend_title_text="<b>Playlist</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>Number of Streams on Spotify</b>"),
                          xaxis2=dict(title_text="<b>Number of Streams on Spotify</b>"),
                          legend=dict(x=0.9,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col7.plotly_chart(fig)
        col6.markdown("")
        col6.markdown("")
        col6.markdown("For Spotify and Apple Music playlists, the graph follows an ascending trend, that the more streams a track receives, the more number of playlists it is likely to be in. For deezer playlists, however, the ascending trend is not very obvious, as many tracks are clustered at low numbers of playlists, and tracks with mid-to-high number of streams are spread out between low to high number of playlists.")
        col6.markdown("From those observations, we see that playlists can certainly be essential for the tracks' success and popularity, so that artists would gain greater exposure in the music industry.")
    
    
    
    st.subheader("Comparing Days & Months of Release")
    col9,col10,col11=st.columns([4,5,5])
    
    with st.form("Box plot: Streams vs. Day & Month"):
        fig_1 = px.box(spotify_graph, x="day_of_week", y="streams", color="day_of_week", color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"], height=600, title="Day of Release vs. Streams on Spotify")
        fig_1.update_traces(marker_line_width=1)
        fig_1.update_xaxes(title_text="<b>Day of Release</b>", title_font_size=14)
        fig_1.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig_1.update_layout(title_x=0.25, legend_title_font_size=14, legend_title_text="<b>Day of Release</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig_1.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        fig_2 = px.box(spotify_graph, x="month_name", y="streams", color="month_name", color_discrete_sequence=color_list, category_orders=order_dict, labels=all_cols_dict, hover_data=["track_name","artists_name"], height=600, title="Month of Release vs. Streams on Spotify")
        fig_2.update_traces(marker_line_width=1)
        fig_2.update_xaxes(title_text="<b>Month of Release</b>", title_font_size=14)
        fig_2.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig_2.update_layout(title_x=0.25, legend_title_font_size=14, legend_title_text="<b>Month of Release</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig_2.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col10.plotly_chart(fig_1)
        col10.plotly_chart(fig_2)
        
        col9.markdown("")
        col9.markdown("")
        col9.markdown("By looking at the median, q3 and upper fence, Tuesday releases have the most streams on Spotify overall, while Thursday and Friday releases also have some tracks that received greater streams.")
        col9.markdown("Friday, however, has the lowest median and lower boundary of them all, though it has several outliers that received the highest streams. This is because Friday is the music industry's global release day since 2015, where many artists release on that day to maximize their sales and increase their popularity. This in turn causes more competition that drives down artists' chance for their songs to be more popular than releases on other days.<sup>9</sup> <sup>10</sup>", unsafe_allow_html=True)
        col9.markdown("")
        col9.markdown("As for Months, January releases have the overall highest number of streams on Spotify, followed by September. November also has some tracks with the highest streams, although its median and upper boundary is less than January and September.")
    


if selected == "Analysis of Artists":
    st.title("Analysis of Artists")
    st.markdown("Now we will focus on 5 of the top artists that have distinctive musical features, while trying to analyze why do they have certain song attributes that made them popular as they are. We will only focus on Energy, Danceability and Valence, as these musical attributes tend to have high or decent levels across a majority of tracks.")
    
    st.subheader("Analysis of Taylor Swift")
    st.markdown("In terms of personality, Taylor Swift is known for being a charitable pop artist, with high empathy, loyalty, and outgoingness. Taylor demonstrates 'emotional intelligence' through her feelings, hurt, and worries in her music to touch the fans. Throuugh her discography, she demonstrates rich personality traits, reflecting her own persona, as well as resonating with her listeners' diverse personality types.<sup>11</sup> <sup>12</sup>", unsafe_allow_html=True)
    
    col1,col2,col3=st.columns([4,5,5])
    
    with st.form("Box plot by Taylor Swift"):
        taylor = melt4[melt4["artists_name"]=="Taylor Swift"]
        fig = px.box(taylor, x="artists_name", y="streams", color="level", color_discrete_sequence=color_list, facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.2, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title="Streams on Spotify vs. Musical Attributes (Taylor Swift)", height=800, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>Taylor Swift's Releases</b>"),
                          legend=dict(x=0.8,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col2.plotly_chart(fig)
        col1.markdown("")
        col1.markdown("")
        col1.markdown("Most of Taylor Swift's popular songs have high levels of energy and decent levels of danceability (with some most-streamed tracks with high danceability), which corresponds to the previous findings of how mid-to-high levels of danceabilty and energy generally made tracks to receive greater streams.")
        col1.markdown("Meanwhile, Taylor has popular tracks with all three levels of valence (and decent having the most streams). Valence measures the musical positiveness of the tracks, of whether the tracks are happy and cheerful when it's a high level, or sad, depressed and angry when it's a low level. The rich personality traits in her music may have covered diverse traits of feelings ranging from joy to sadness, as shown as the levels of valence among her popular songs.")
    
    
    
    st.subheader("Analysis of Eminem")
    st.markdown("Eminem is recognized as a very observant, adaptable and flexible artist, who experiments with different musical styles and themes throughout his career. Eminem's music, performances, and lyrical content can be described as 'intense', 'rebellious' and 'independent', as he is known for an individualistic approach to his music that constantly challenging and resisting societal expectations and norms.<sup>13</sup>", unsafe_allow_html=True)
    
    col12,col13,col14=st.columns([4,5,5])
    
    with st.form("Box plot by Eminem"):
        eminem = melt4[melt4["artists_name"]=="Eminem"]
        fig = px.box(eminem, x="artists_name", y="streams", color="level", color_discrete_sequence=color_list, facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.2, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title="Streams on Spotify vs. Musical Attributes (Eminem)", height=800, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>Eminem's Releases</b>"),
                          legend=dict(x=0.8,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col13.plotly_chart(fig)
        col12.markdown("")
        col12.markdown("")
        col12.markdown("Likely because of Eminem's intensity, the popular releases on Spotify only has high energy levels, with no decent and low energy levels. Eminem has more popular tracks with high levels of danceability, but decent danceability tracks have a greater q1, median and q3 of streams. It is likely because of how Eminem experiments with different levels of danceability in his music, while some tracks with high and decent danceability becomes his most popular ones.")
        col12.markdown("Eminem, though, has most-streamed tracks in highest and lowest valence levels. It is likely because that Eminem's individualistic approach to his music made him to have more widely recognized songs that are highly joyful and cheerful, or that are more depressed and filled with anger.")
    
    
    
    st.subheader("Analysis of Justin Bieber")
    st.markdown("Justin Bieber is known for one of the most giving celebrities, because of his altruism from supporting numerous charities. Bieber is being described as passionate and emotionally sensitive (being photographed sobbing on a city bike, had emotional breakdown during the VMAs, etc.), with his music capturing his emotional sensitivity alongside his artistry and creativity. The songs reflect his character as his sensitive lyrics, energetic beats, as well as flexible music style.<sup>14</sup>", unsafe_allow_html=True)
    
    col4,col5,col6=st.columns([4,5,5])
    
    with st.form("Box plot by Justin Bieber"):
        bieber = melt4[melt4["artists_name"]=="Justin Bieber"]
        fig = px.box(bieber, x="artists_name", y="streams", color="level", color_discrete_sequence=color_list, facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.2, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title="Streams on Spotify vs. Musical Attributes (Justin Bieber)", height=800, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>Justin Bieber's Releases</b>"),
                          legend=dict(x=0.8,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col5.plotly_chart(fig)
        col4.markdown("")
        col4.markdown("")
        col4.markdown("Justin Bieber's energetic beats made most of his popular tracks to have high levels of energy. His flexible music style made most of his tracks to have decent levels of danceability (while having some tracks with high), meaning that he doesn't only stick to 'danceable' music. Again, it fits the previous findings of high levels of energy making tracks to receive higher streams.")
        col4.markdown("Being emotionally sensitive, Bieber's popular tracks mostly have decent levels of valence, meaning that they have either moderate levels of happiness, or sadness and anger. There are also tracks with high levels of valence, although they have lower streams.")
    
    
    
    st.subheader("Analysis of Dua Lipa")
    st.markdown("Dua Lipa has been known for her upbeat and dance songs. As pop music was dominated by the downbeat songs of aggrieved and sadness, Dua Lipa came with her dancey and joyous-sounding tracks, to change the scene of pop music, even when the song is about a break-up. Dua Lipa's persona is slightly mysterious, yet everyone can feel her genuine personality, and her authenticity, through her music.<sup>15</sup>", unsafe_allow_html=True)
    
    col4,col5,col6=st.columns([4,5,5])
    
    with st.form("Box plot by Dua Lipa"):
        dua = melt4[melt4["artists_name"]=="Dua Lipa"]
        fig = px.box(dua, x="artists_name", y="streams", color="level", color_discrete_sequence=color_list, facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.2, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title="Streams on Spotify vs. Musical Attributes (Dua Lipa)", height=800, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>Dua Lipa's Releases</b>"),
                          legend=dict(x=0.8,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col5.plotly_chart(fig)
        col4.markdown("")
        col4.markdown("")
        col4.markdown("As Dua Lipa is known for her upbeat and dance songs, it is obvious that all her songs have high levels of danceability, with vast majority of her songs having high levels of energy.")
        col4.markdown("Most of Dua Lipa's popular songs have high levels of valence, although tracks with decent valence generally have more streams. As her popular tracks are mostly joyous-sounding, most of it have high valence levels, and even her break-up songs made it to decent valence instead of low.")
    
    
    
    st.subheader("Analysis of BTS")
    st.markdown("BTS, being identified as K-pop group, has a versatile discography with diverse musical styles throughout the years, ranging from rap/hip hop and dance tracks to ballads. BTS spans several languages (including Korean, English and Japanese) that attracts a global audience, with their music having uplifting messages and speaking up on important issues, including mental health awareness and self-love.<sup>16</sup> <sup>17</sup>", unsafe_allow_html=True)
    
    col4,col5,col6=st.columns([4,5,5])
    
    with st.form("Box plot by BTS"):
        bts = melt4[melt4["artists_name"]=="BTS"]
        fig = px.box(bts, x="artists_name", y="streams", color="level", color_discrete_sequence=color_list, facet_col="factors", facet_col_wrap=2, facet_row_spacing=0.2, category_orders=order_dict, labels=all_cols_dict, hover_data="track_name",title="Streams on Spotify vs. Musical Attributes (BTS)", height=800, width=800)
        fig.update_traces(marker_line_width=1)
        fig.update_yaxes(title_text="<b>Number of Streams on Spotify</b>", title_font_size=14)
        fig.update_layout(title_x=0.2, legend_title_font_size=14, legend_title_text="<b>Level</b>", legend_bordercolor="green", legend_borderwidth=2, hoverlabel_font_size=14)
        fig.update_layout(xaxis=dict(title_text="<b>BTS' Releases</b>"),
                          legend=dict(x=0.8,y=0.3,xanchor='right',yanchor='top'))
        fig.for_each_annotation(lambda a: a.update(text=f'<b>{a.text.split("=")[-1]}</b>',font_size=14))
        
        col5.plotly_chart(fig)
        col4.markdown("")
        col4.markdown("")
        col4.markdown("Many of the popular BTS tracks have high and decent levels of danceability and energy, while decent danceaiblity and energy tracks receive the highest streams overall. In fact, BTS' versatility in musical styles made them to be known by not just 'danceable' and 'highly energetic' music.")
        col4.markdown("BTS' music also covered all three levels of valence, with the decent ones having the highest streams overall, while high valence tracks are also quite common. Their high to decent level of valence (happy, joyful, and not so much sadness) may correspond to their uplifting messages in their music, as well as their lyrical themes including mental health awareness and self-love, which also contributes to their musical positivity.")
    
    st.markdown("Overall, most of the artists follow the previously identified patterns, wherein mid-to-high levels of Danceability and Energy tend to make their tracks more popular. However, it depends on the artists' style and musical characteristics that are most well-known for. Valence alone may not have a significant impact on the popularity of tracks. However, it is the artists' personal traits, musical style, and lyrical themes, which they are known for, that determines the level of valence and generates popularity for their tracks. Hence, artists themselves can certainly influence and determine the popularity of songs.")




if selected=="Conclusion":
    st.title("Conclusion")
    
    st.markdown("Based on the explorations and analysis, tracks with a decent to high amount of danceability and energy, low levels of acousticness and speechiness, are all general factors that made these tracks popular as it is today. Among the most-streamed tracks, valence can be spread out from high to low levels. Tracks in Major keys of C#, D and F# also has a great number of streams on Spotify.")
    st.markdown("The popularity of a song can also be influenced by the number of playlists it is included in. The more playlists a song is featured on, the greater exposure it receives, especially on platforms like Spotify. Additionally, tracks released on Tuesdays, Thursdays, and Fridays, as well as in the months of January, September, and November, are more likely to be popular compared to releases on other days or months. However, if a song is released during highly competitive times, such as on a Friday when many artists are also releasing new material, it is likely to lower the chance for becoming popular songs.")
    st.markdown("By analyzing certain artists, we found that the song's artist(s) can certainly influence the song's popularity based on the persona, style, and musical and lyrical traits that the artist is known for. These traits are also reflected in their musical attributes, including danceability, valence, and energy. The artist's persona, style, and musical qualities, shown as their leels of danceability, valence and energy, can attract and resonate with specific audiences, contributing to the success of their songs.")
    st.markdown("Most of the observations align with past studies and claims made by experts, except for the aspects of Mode and Key. This suggests that audience preferences for the specified musical attributes have remained relatively consistent over recent years. However, there may have been some changes in the preferences for the Mode and Key of songs.")
    st.markdown("The above results outline the 'scientific' factors that contribute to certain tracks being more popular than others, as well as the user preferences for popular songs as of 2023. Through this case study, we have gained a better understanding of the specific user preferences for songs and the musical traits that many people loves. Hopefully, now we've understood why we enjoy certain songs that we listen to today!")

    




if selected=="Bibliography":
    st.title("Bibliography")
    st.markdown("The dataset is downloaded from https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023, date accessed, 2023-12-20")
    st.markdown("[1] About Spotify, https://newsroom.spotify.com/company-info/, date accessed, 2023-12-20")
    st.markdown("[2] How we generate popular tracks, https://support.spotify.com/us/artists/article/how-we-generate-popular-tracks/, date accessed, 2023-12-20")
    st.markdown("[3] What Makes a Song Likeable?, Ashrith, Dec 4, 2018, https://towardsdatascience.com/what-makes-a-song-likeable-dbfdb7abe404")
    st.markdown("[4] What are factors that make song in Spotify popular?, Ravee Virojsirasak, Oct 16, 2021, https://medium.com/@sunsunvirojsirasak/what-are-factors-that-make-song-in-spotify-popular-3cdcb3fb3a10")
    st.markdown("[5] What makes a song a hit?, Rachel Drysdale, Jul 16, 2021, https://medium.com/@racheldrysdale_/what-makes-a-song-a-hit-9d8eb4512639")
    st.markdown("[6] Apple Music vs. Spotify: Which music streaming service is the best?, Michael Bizzaco , Tyler Lacoma and Amanda Blain, Nov 29, 2023, https://www.digitaltrends.com/mobile/apple-music-vs-spotify/")
    st.markdown("[7] Best free music apps 2023: free music on Android and iPhone, Harry McKerrell, Nov 18, 2023, https://www.whathifi.com/best-buys/best-free-music-apps-free-music-on-android-and-iphone")
    st.markdown("[8] Best Day To Release Music: Your Success in the Music Industry, Josh McKenzie, Apr 14, 2023, https://www.cdunity.com/best-day-to-release-music/")
    st.markdown("[9] Why Do We Release Music On Fridays?, https://www.otherrecordlabels.com/why-do-we-release-music-on-fridays, date accessed, 2023-12-20")
    st.markdown("[10] Best Day To Release Music On Spotify: The Answer May Surprise You!, Grizzly Beatz, Oct 16, 2021, https://www.grizzlybeatz.com/lofi-hip-hop-blog/best-day-to-release-music-on-spotify-the-answer-may-surprise-you")
    st.markdown("[11] Taylor Swift Personality Type, Traits, and MBTI Analysis, Alexandru Ion, March 25, 2023, https://www.thecoolist.com/personality/types/celebrity/taylor-swift/")
    st.markdown("[12] Taylor Swift Songs As Personality Types, Lyle Opolentisima, Oct 20, 2023, https://dailyinfographic.com/taylor-swift-songs-as-personality-types")
    st.markdown("[13] Eminem Personality Type, Traits, and MBTI Analysis, Theresa Schramm, May 27, 2023, https://www.thecoolist.com/personality/types/celebrity/eminem/")
    st.markdown("[14] Justin Bieber Personality Type, Traits, and MBTI Analysis, Alexandru Ion, Jan 31, 2023, https://www.thecoolist.com/personality/types/celebrity/justin-bieber/")
    st.markdown("[15] New Rules: Dua Lipa Is Changing Pop Music, Here's How, ANGELA NATIVIDAD, Jun 7, 2022, https://www.thethings.com/heres-how-dua-lipa-is-changing-the-rules-of-pop-music/")
    st.markdown("[16] What it means when we say BTS is the Genre, Alexandra Nae, Jun 25, 2021, https://enthralledbookworm.wordpress.com/2021/06/25/what-it-means-when-we-say-bts-is-the-genre/")
    st.markdown("[17] Why Is BTS So Popular? 9 Questions About The K-Pop Phenoms Answered, ASHLEE MITCHELL, May 28, 2022, https://dailyinfographic.com/taylor-swift-songs-as-personality-types")
