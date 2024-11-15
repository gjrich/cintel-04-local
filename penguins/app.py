# Previous imports and data preparation code remains the same until the header section
import plotly.express as px
from shiny.express import input, ui, output, render
from shinywidgets import render_plotly, render_widget
from shiny import reactive
import palmerpenguins
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Load and prepare data
penguin_df = palmerpenguins.load_penguins()

# Get unique values and ranges for UI choices
species_choices = sorted(penguin_df['species'].unique().tolist())
island_choices = sorted(penguin_df['island'].unique().tolist())
sex_choices = sorted(penguin_df['sex'].dropna().unique().tolist())
mass_min = int(penguin_df['body_mass_g'].min())
mass_max = int(penguin_df['body_mass_g'].max())

# Set some style configurations
plt.style.use('seaborn-darkgrid')
custom_colors = px.colors.qualitative.Set3

# Main UI layout
ui.page_opts(
    title="Palmer Penguins Dashboard",
    fillable=True
)

# Add header with improved layout
# Add header with improved layout
with ui.layout_columns():
    with ui.card(style="background-color: #2c3e50; color: white; height: 80px; overflow: hidden;"):
        with ui.div(class_="d-flex justify-content-between align-items-center", style="height: 100%; padding: 0 20px;"):
            ui.h2("Palmer Penguins Dashboard", style="margin: 0;")
            ui.h4("🐧 Just Chillin' with Some Cool Data! 🧊", style="color: #95a5a6; margin: 0;")


# Data tables in collapsed cards
with ui.layout_columns():
    with ui.card():
        with ui.accordion(id="data_accordion"):
            with ui.accordion_panel("View Raw Data Tables"):
                with ui.layout_columns(cols=2):
                    with ui.card():
                        "Penguin Data Table"
                        @render.data_frame
                        def penguintable():
                            return render.DataTable(penguin_df, filters=False, height="200px")
                    
                    with ui.card():
                        "Penguin Data Grid"
                        @render.data_frame
                        def penguingrid():
                            return render.DataGrid(penguin_df, filters=False, height="200px")

# Sidebar with increased width and fixed styling
with ui.sidebar(open="open"):
    
    ui.div(
        style="background-color: #34495e; padding: 10px; border-radius: 5px; margin: 10px 0;",
        class_="h-100"
    )
    ui.h3("🐧 Control Panel")
    
    ui.input_selectize(
        "selected_attribute",
        "Select Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
        width="100%"
    )
    
    ui.input_numeric(
        "plotly_bin_count",
        label="Plotly hist bin count",
        value=15,
        min=2,
        max=50
    )
    
    ui.input_slider(
        "seaborn_bin_count",
        label="Seaborn hist bin count",
        min=2,
        max=50,
        value=15
    )
    
    ui.hr()
    
    ui.div(
        ui.input_checkbox_group(
            "selected_species_list",
            label="Species Filter",
            choices=species_choices,
            selected=[species_choices[0]],
            inline=True,
        ),
        id="species-filter-group",
        style="background-color: #34495e; padding: 10px; border-radius: 5px; margin: 10px 0;"
    )
    
    ui.div(
        ui.input_checkbox_group(
            "selected_island_list",
            label="Island Filter",
            choices=island_choices,
            selected=[island_choices[0]],
            inline=True,
        ),
        id="island-filter-group",
        style="background-color: #34495e; padding: 10px; border-radius: 5px; margin: 10px 0;"
    )
    
    ui.div(
        ui.input_checkbox_group(
            "selected_sex_list",
            label="Sex Filter",
            choices=sex_choices,
            selected=sex_choices,
            inline=True,
        ),
        id="sex-filter-group",
        style="background-color: #34495e; padding: 10px; border-radius: 5px; margin: 10px 0;"
    )
    
    ui.input_slider(
        "mass_min_max_range",
        "Mass Range (g)",
        min=mass_min,
        max=mass_max,
        value=[mass_min, mass_max]
    )
    
    ui.hr()
    ui.a(
        "📊 gjrich github",
        href="https://github.com/gjrich/cintel-03-reactive/",
        target="_blank",
        style="color: #3498db;"
    )
    
    
    
# CSS editing for filter groups
ui.tags.style("""
    #species-filter-group label,
    #island-filter-group label,
    #sex-filter-group label {
        color: white;
    }
""")
    
# Reactive function to filter data
@reactive.Calc
def filtered_data() -> pd.DataFrame:
    try:
        filtered_df = penguin_df.copy()
        
        # Apply filters
        selected_species = [s.lower() for s in input.selected_species_list()]
        filtered_df = filtered_df[filtered_df["species"].str.lower().isin(selected_species)]
        
        selected_island = [i.lower() for i in input.selected_island_list()]
        filtered_df = filtered_df[filtered_df["island"].str.lower().isin(selected_island)]
        
        selected_sex = [s.lower() for s in input.selected_sex_list()]
        filtered_df = filtered_df[filtered_df["sex"].str.lower().isin(selected_sex)]
        
        selected_min_mass, selected_max_mass = input.mass_min_max_range()
        filtered_df = filtered_df[
            (filtered_df["body_mass_g"] <= selected_max_mass) & 
            (filtered_df["body_mass_g"] >= selected_min_mass)
        ]
        
        return filtered_df if not filtered_df.empty else penguin_df
        
    except Exception as e:
        print(f"Error in filtered_data: {e}")
        return penguin_df

# Visualizations with improved styling
with ui.layout_columns(fills=True):
    with ui.card():
        ui.card_header("📊 Plotly Histogram", style="background-color: #2c3e50; color: white;")
        @render_widget
        def plot1():
            return px.histogram(
                data_frame=filtered_data(),
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count(),
                color_discrete_sequence=[custom_colors[0]]
            ).update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title={"text": f"Distribution of {input.selected_attribute()}", "x": 0.5},
                yaxis_title="Count",
                xaxis_title=input.selected_attribute().replace('_', ' ').title(),
                showlegend=False
            )

    with ui.card():
        ui.card_header("📈 Seaborn Histogram", style="background-color: #2c3e50; color: white;")
        @render.plot
        def plot2():
            plt.clf()
            fig, ax = plt.subplots(figsize=(8, 6))
            ax = sns.histplot(
                data=filtered_data(),
                x=input.selected_attribute(),
                bins=input.seaborn_bin_count(),
                color="#55A868"  # Using a specific hex color
            )
            ax.set_title(f"Distribution of {input.selected_attribute().replace('_', ' ').title()}")
            ax.set_xlabel(input.selected_attribute().replace('_', ' ').title())
            ax.set_ylabel("Count")
            plt.tight_layout()
            return fig

with ui.layout_columns(fills=True):
    with ui.card():
        ui.card_header("🔍 Species Comparison", style="background-color: #2c3e50; color: white;")
        @render_plotly
        def plotly_scatterplot():
            data = filtered_data()
            if not data.empty:
                return px.scatter(
                    data_frame=data,
                    x="bill_length_mm",
                    y="bill_depth_mm",
                    color="island",
                    symbol="species",
                    labels={
                        "bill_depth_mm": "Bill Depth (mm)",
                        "bill_length_mm": "Bill Length (mm)",
                        "species": "Species",
                        "island": "Island"
                    }
                ).update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    title={"text": "Bill Dimensions by Species and Island", "x": 0.5}
                )
            else:
                return px.scatter()

    with ui.card():
        ui.card_header("⚖️ Mass Distribution", style="background-color: #2c3e50; color: white;")
        @render.plot
        def seaborn_histogram():
            plt.clf()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(
                data=filtered_data(),
                x="body_mass_g",
                bins=input.seaborn_bin_count(),
                color="#4C72B0"  # Using a specific hex color
            )
            plt.title("Distribution of Penguin Mass")
            plt.xlabel("Mass (g)")
            plt.ylabel("Count")
            plt.tight_layout()
            return fig