# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Sun Nov 26 12:29:33 2023
# @author: gustavoborda
# """



import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Enhanced Player Scatterplot', page_icon="chart_with_upwards_trend", layout='wide')

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    excel_data = pd.ExcelFile(uploaded_file)
    sheet_names = excel_data.sheet_names

    selected_sheet = st.selectbox("Select a sheet", sheet_names)

    if selected_sheet:
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        st.sidebar.header('Scatterplot Options:')

        # Check for the presence of 'Jugador' and 'Equipo'
        if 'Jugador' in df.columns:
            use_jugador = True
            st.sidebar.subheader("Using 'Jugador' and 'Minutos jugados'")
        elif 'Equipo' in df.columns:
            use_jugador = False
            st.sidebar.subheader("Using 'Equipo'")

        # Choose X and Y variables for scatterplot
        x_var = st.sidebar.selectbox("Select X variable:", df.columns[1:])
        y_var = st.sidebar.selectbox("Select Y variable:", df.columns[1:])

        # Slider for filtering by minutes played only if using Jugador
        if use_jugador:
            min_minutes, max_minutes = st.sidebar.slider(
                "Select minutes played range:",
                min_value=int(df['Minutos jugados'].min()),
                max_value=int(df['Minutos jugados'].max()),
                value=(int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max())),
                step=1
            )
            # Filter the data based on the slider
            df = df[(df['Minutos jugados'] >= min_minutes) & (df['Minutos jugados'] <= max_minutes)]
        
        # Checkbox to toggle players with zero values
        filter_zeros = st.sidebar.checkbox("Exclude players with zero values")

        # Further filter the data based on the checkbox
        if filter_zeros:
            df = df[(df[x_var] != 0) & (df[y_var] != 0)]

        # Choose player to highlight based on what is being used
        if use_jugador:
            highlight_player = st.sidebar.selectbox("Select Player to Highlight:", df['Jugador'].unique())
        else:
            highlight_player = st.sidebar.selectbox("Select Team to Highlight:", df['Equipo'].unique())

        # Calculate mean for x and y to create quadrants
        x_mean = df[x_var].mean()
        y_mean = df[y_var].mean()

        # Add a column for marker color based on player or team highlight
        if use_jugador:
            df['Color'] = ['#7a33ff' if player == highlight_player else 'skyblue' for player in df['Jugador']]
        else:
            df['Color'] = ['#7a33ff' if team == highlight_player else 'skyblue' for team in df['Equipo']]

        # Create interactive scatterplot with Plotly
        fig = px.scatter(
            df,
            x=x_var,
            y=y_var,
            color='Color',
            color_discrete_map={"#7a33ff": "#7a33ff", "skyblue": "skyblue"},
            hover_name='Jugador' if use_jugador else 'Equipo',  # Display name on hover
            title=f"{x_var} vs {y_var} Scatterplot",
            labels={x_var: x_var, y_var: y_var},
            
        )

        # Add quadrant lines at mean values
        fig.add_vline(x=x_mean, line_width=1, line_dash="dash", line_color="gray")
        fig.add_hline(y=y_mean, line_width=1, line_dash="dash", line_color="gray")

        # Customize layout for aesthetics
        fig.update_layout(
            xaxis_title=x_var,
            yaxis_title=y_var,
            title={
                'text': f"{x_var} vs {y_var} Scatterplot",
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend_title_text='Player/Team Highlight',
            showlegend=False
        )

        # Display Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
