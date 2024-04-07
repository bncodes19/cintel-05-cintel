from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# Constant update interval for live data set to every 3 seconds
UPDATE_INTERVAL_SECS: int = 3

# Initialize reactive value with common data structure
DEQUE_SIZE: int = 10
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))


# Initialize a reactive calc that all display components can call
@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic
    temp = round(random.uniform(50, 60), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_dictionary_entry = {"temp":temp, "timestamp":timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry

# Shiny UI Page layout
ui.page_opts(title="Live Temperature Dashboard", fillable=True)

# Dashboard sidebar content
with ui.sidebar(position="right", bg="#f8f8f8", open="open"):

    ui.h2("Kansas Temperatures", class_="text-center")
    ui.p("A demonstration of real-time temperature readings in Kansas.",class_="text-center")
    ui.hr()
    ui.h5("Project Links:")
    ui.a("GitHub Source",href="https://github.com/bncodes19/cintel-05-cintel",target="_blank")
    ui.a("README.md", href="https://github.com/bncodes19/cintel-05-cintel/blob/main/README.md", target="_blank")
    ui.a("app.py", href="https://github.com/bncodes19/cintel-05-cintel/blob/main/app.py", target="_blank")
    ui.a("requirements.txt", href="https://github.com/bncodes19/cintel-05-cintel/blob/main/requirements.txt", target="_blank")


# Dashboard main content
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("sun"),
        theme="bg-gradient-red-cyan",
    ):
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} F"
        "warmer than usual"
    with ui.value_box(
        showcase=icon_svg("clock"),
        theme="bg-gradient-purple-cyan",
    ):
        "Current Date and Time"
        @render.text
        def display_current_date_time():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"    
  
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)
            return render.DataGrid( df,width="100%")

with ui.card():
    ui.card_header("Chart with Current Trend")

    @render_plotly
    def display_plot():
        # Fetch from the reactive calc function
        deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()

        # Ensure the DataFrame is not empty before plotting
        if not df.empty:
            # Convert the 'timestamp' column to datetime for better plotting
            df["timestamp"] = pd.to_datetime(df["timestamp"])
 
            fig = px.scatter(df,
            x="timestamp",
            y="temp",
            title="Temperature Readings with Regression Line",
            labels={"temp": "Temperature (°F)", "timestamp": "Time"},
            color_discrete_sequence=["blue"] )
            
            # For x let's generate a sequence of integers from 0 to len(df)
            sequence = range(len(df))
            x_vals = list(sequence)
            y_vals = df["temp"]

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
            df['best_fit_line'] = [slope * x + intercept for x in x_vals]

            # Add the regression line to the figure
            fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

            # Update layout as needed to customize further
            fig.update_layout(xaxis_title="Time",yaxis_title="Temperature (°C)")

        return fig
