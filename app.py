# Gabriel Richards
# November 2024
# Filtering the Palmer Penguins dataset using Shiny

# Shiny App created for use in Shinylive:
# https://shinylive.io/py/examples/#plotly

# To use, paste packages in requirements.txt and code from this app.py into the matching tabs in the link above, and then run the code.
# Please send any issues or recommendations you find to gabrieljrich@pm.me


import plotly.express as px
from shiny.express import input, ui, output, render
from shinywidgets import render_plotly, render_widget
from shiny import reactive
import palmerpenguins  # This package provides the Palmer Penguins dataset
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


# Use the built-in function to load the Palmer Penguins dataset
# Columns include:
# - species: chinstrap, adelie, and gentoo
# - island: island name: Dream, torgensen, or Biscoe - islands in the Palmer Archipelago
# - bill_length_mm: length of bill in millimeters (mm)
# - bill_depth_mm: depth of bill in millimeters (mm)
# - flipper_length_mm: flipper length in millimeters (mm)
# - body_mass_g: body mass in grams (g)
# - sex: male or female

# it is then loaded into a pandas dataframe
penguin_df = palmerpenguins.load_penguins()


with ui.layout_columns():
    # Data Table
    with ui.card():
        "Penguin Data Table"
        @render.data_frame
        def penguintable():
            return render.DataTable(penguin_df, filters=False)

    # Data Grid
    with ui.card():
        "Penguin Data Grid"
        @render.data_frame
        def penguingrid():
            return render.DataGrid(penguin_df, filters=False)


# Add a Shiny UI sidebar for user interaction
# Use the ui.sidebar() function to create a sidebar
# Set the open parameter to "open" to make the sidebar open by default
# Use a with block to add content to the sidebar
with ui.sidebar(open="open"):
    
    # Use the ui.h2() function to add a 2nd level header to the sidebar
    #   pass in a string argument (in quotes) to set the header text to "Sidebar"
    ui.h2("Sidebar")


    # Use ui.input_selectize() to create a dropdown input to choose a column
    #   pass in three arguments:
    #   the name of the input (in quotes), e.g., "selected_attribute"
    #   the label for the input (in quotes)
    #   a list of options for the input (in square brackets) 
    #   e.g. ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    ui.input_selectize(
        "selected_attribute", "Select Attribute", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    )

    # Use ui.input_numeric() to create a numeric input for the number of Plotly histogram bins
    #   pass in two arguments:
    #   the name of the input (in quotes), e.g. "plotly_bin_count"
    #   the label for the input (in quotes)
    ui.input_numeric("plotly_bin_count", label="Plotly hist bin count", value=10, min=2, max=50)


    # Use ui.input_slider() to create a slider input for the number of Seaborn bins
    #   pass in four arguments:
    #   the name of the input (in quotes), e.g. "seaborn_bin_count"
    #   the label for the input (in quotes)
    #   the minimum value for the input (as an integer)
    #   the maximum value for the input (as an integer)
    #   the default value for the input (as an integer)
    ui.input_slider("seaborn_bin_count", label="Seaborn hist bin count", min=2, max=50, value=10) 

    ui.hr()
    
    # Use ui.input_checkbox_group() to create a checkbox group input to filter the species
    #   pass in five arguments:
    #   the name of the input (in quotes), e.g.  "selected_species_list"
    #   the label for the input (in quotes)
    #   a list of options for the input (in square brackets) as ["Adelie", "Gentoo", "Chinstrap"]
    #   a keyword argument selected= a list of selected options for the input (in square brackets)
    #   a keyword argument inline= a Boolean value (True or False) as you like
    ui.input_checkbox_group("selected_species_list", label="Filter Species", choices=["Adelie", "Chinstrap","Gentoo"], selected=["Adelie"],inline=False)

    ui.input_checkbox_group("selected_island_list", label="Filter Island", choices=["Biscoe", "Dream","Torgersen"], selected=["Biscoe"],inline=False)

    ui.input_checkbox_group("selected_sex_list", label="Filter Sex", choices=["Male", "Female"], selected=["Male", "Female"],inline=False)

    ui.input_slider("mass_min_max_range", "Filter by Mass (g)", min=2500, max=6500, value=[2500,6000])

    # Use ui.hr() to add a horizontal rule to the sidebar
    ui.hr()

    # Use ui.a() to add a hyperlink to the sidebar
    #   pass in two arguments:
    #   the text for the hyperlink (in quotes), e.g. "GitHub"
    #   a keyword argument href= the URL for the hyperlink (in quotes), e.g. your GitHub repo URL
    #   a keyword argument target= "_blank" to open the link in a new tab
    ui.a("gjrich - github", href="https://github.com/gjrich/cintel-03-reactive/")

# Filter the dataset 
@reactive_calc
def filtered_data() -> pd.DataFrame:
    
    # Filter penguin_df based on selected species & island
    selected_species = input.selected_species_list()  # Get the selected species from the checkbox group
    filtered_df = penguin_df[penguin_df["species"].isin(selected_species)]
    selected_island = input.selected_island_list() # get selected island from checkbox group
    filtered_df = filtered_df[filtered_df["island"].isin(selected_island)]

    # Filter based on sex
    selected_sex = input.selected_sex_list()
    filtered_df = filtered_df[filtered_df["sex"].isin(selected_sex)]

    # Filter based on body mass
    selected_min_mass, selected_max_mass = input.mass_min_max_range()
    filtered_df = filtered_df[(filtered_df["body_mass_g"] <= selected_max_mass) & (filtered_df["body_mass_g"] >= selected_min_mass)]
    
    if filtered_df.empty:
        return pd.DataFrame()
    
    return filtered_df



# Build the UI
ui.page_opts(title="gjrich's penguin review", fillable=True)
with ui.layout_columns():

    with ui.card():
        ui.card_header("Plotly Histogram")
        @render_widget
        def plot1():
            scattery = px.histogram(
                data_frame=penguin_df,
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count()
            ).update_layout(title={"text": "Penguins", "x": 0.5}, yaxis_title="count",xaxis_title=input.selected_attribute())
            return scattery


    
    with ui.card():
        ui.card_header("Seaborn Histogram")
        @render.plot
        def plot2():
            ax=sns.histplot(data=filtered_df, x=input.selected_attribute(), bins=input.seaborn_bin_count())
            ax.set_title("Penguins")
            ax.set_xlabel(input.selected_attribute())
            ax.set_ylabel("Count")
            return ax

    with ui.card():
        ui.card_header("Plotly Scatterplot: Species")
        @render_plotly
        def plotly_scatterplot():
                        
            return px.scatter(
                data_frame=filtered_df,
                x="bill_length_mm",
                y="bill_depth_mm",
                color="island",
                symbol="species",
                labels={"bill_depth_mm": "Bill Depth (mm)",
                       "bill_length_mm": "Bill Length (mm)",
                       "species": "Species of Penguin",
                       "island": "Island of origin"},
            )
    
    # --------------------------------------------------------
    # Reactive calculations and effects
    # --------------------------------------------------------

    # Add a reactive calculation to filter the data
    # By decorating the function with @reactive, we can use the function to filter the data
    # The function will be called whenever an input functions used to generate that output changes.
    # Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

    with ui.card():
        ui.card_header("Reactive Calc")

        @render.plot(alt="A Seaborn histogram on penguin body mass in grams.")
        def seaborn_histogram():
                    histplot = sns.histplot(data=filtered_df, x="body_mass_g", bins=input.seaborn_bin_count() )
                    histplot.set_title("Palmer Penguins")
                    histplot.set_xlabel("Mass (g)")
                    histplot.set_ylabel("Count")
                    return histplot
                
                
# Bonus Notes:
# Decorators
# ----------
# Use the @ symbol to decorate a function with a decorator.
# Decorators a concise way of calling a function on a function.
# We don't typically write decorators, but we often use them.
