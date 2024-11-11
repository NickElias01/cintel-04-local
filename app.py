# ------------------------------------------------------------------------------
# Penguin Data Exploration Dashboard
#  Nick Elias - Elias Analytics
# ------------------------------------------------------------------------------
# A Shiny for Python app to explore and visualize the Palmer Penguins dataset.
# Users can interactively filter the data and view the following visualizations:
# - Data Table: Display filtered penguin data.
# - Data Grid: Alternative grid view of the data.
# - Plotly Histogram: Distribution of a selected attribute.
# - Plotly Scatter Plot: Relationship between selected attribute and body mass.
# - Seaborn Histogram: Attribute distribution with KDE by species.
#
# Key Libraries:
# - plotly, seaborn: Visualizations.
# - shiny: Reactive UI and interactivity.
# - pandas: Data manipulation.
# - palmerpenguins: Dataset.
# ------------------------------------------------------------------------------


# Standard Library Imports
import logging

# Third-Party Imports
import pandas as pd
import plotly.express as px
import seaborn as sns
from palmerpenguins import load_penguins

# Shiny for Python Imports
from shiny import reactive
from shiny.express import input, render, ui
from shinywidgets import render_plotly, render_widget
from shinyswatch import theme


# Set up logging configuration
logging.basicConfig(level=logging.INFO)


# Define error handling helper function
def validate_data(data, selected_attribute):
    """Check if data is empty or contains NaN values for the selected attribute."""
    # Check if the data is empty or all values are NaN
    if data.empty or data.isnull().all(axis=None):
        logging.warning("The filtered data is empty or contains only NaN values.")
        return False

    # Check if the selected attribute contains NaN values
    if data[selected_attribute].isnull().any():
        logging.warning(
            f"Selected attribute '{selected_attribute}' contains NaN values."
        )

    return True


# Load the penguins dataset
penguins_df = load_penguins()

# Dictionary for formatting attribute names
attribute_labels = {
    "bill_length_mm": "Bill Length (mm)",
    "bill_depth_mm": "Bill Depth (mm)",
    "flipper_length_mm": "Flipper Length (mm)",
    "body_mass_g": "Body Mass (g)",
}

# Reverse dictionary for mapping formatted labels back to raw attribute names
attribute_reverse_map = {v: k for k, v in attribute_labels.items()}


# Define a reactive calculation for data filtering
@reactive.calc
def filtered_data() -> pd.DataFrame:
    """Filter penguins dataset based on selected species and island."""
    # Filter based on selected species list
    filtered_df = penguins_df[
        penguins_df["species"].isin(input.selected_species_list())
    ]

    # Filter based on selected island list
    filtered_df = filtered_df[filtered_df["island"].isin(input.selected_island_list())]

    return filtered_df


# --------------------------------------------------------
# User Interface Section
# --------------------------------------------------------

# Define UI options with Shiny Express and set the main container as scrollable
ui.page_opts(
    title="Elias Analytics - Penguin Data",
    fillable=True,
    style="max-height: 90vh; overflow-y: scroll; padding: 10px;",
    fullwidth=True,
    theme=theme.lux,
)

# Sidebar for user interactions and selections
with ui.sidebar(open="open", bg="#CCE7FF"):
    ui.h2("Options")

    # Dropdown for selecting penguin attributes for analysis
    ui.input_selectize(
        "selected_attribute",
        "Select Penguin Attribute:",
        list(attribute_labels.values()),  # Use the formatted labels
    )

    # Numeric input for controlling the number of bins in the Plotly histogram
    ui.input_numeric(
        "plotly_bin_count",
        "Plotly Histogram Bins:",
        10,  # Default value
        min=1,
        max=100,
    )

    # Slider for setting the number of bins in the Seaborn histogram
    ui.input_slider(
        "seaborn_bin_count", "Seaborn Histogram Bins:", min=5, max=50, value=20
    )

    # Checkbox group for filtering the dataset by penguin species
    ui.input_checkbox_group(
        "selected_species_list",
        "Filter by Species:",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=False,
    )

    # Checkbox group for filtering the dataset by penguin island
    ui.input_checkbox_group(
        "selected_island_list",
        "Filter by Island:",
        ["Biscoe", "Dream", "Torgersen"],  # List of islands in the dataset
        selected=["Biscoe", "Dream", "Torgersen"],  # Default selected islands
        inline=False,  # Set inline to False to stack the checkboxes vertically
    )

    # Horizontal rule for visual separation
    ui.hr()

    # Link to GitHub repository for additional resources
    ui.a(
        "Link to GitHub",
        href="https://github.com/NickElias01/cintel-03-reactive",
        target="_blank",
    )

# --------------------------------------------------------
# Main Content Area
# --------------------------------------------------------

with ui.layout_columns(fill=True):

    # Data Table Card
    with ui.card(full_screen=True):
        ui.h3("Penguin Data Table")

        @render.data_frame
        def penguins_datatable():
            return render.DataTable(filtered_data())

    # Data Grid Card
    with ui.card(full_screen=True):
        ui.h3("Penguin Data Grid")

        @render.data_frame
        def penguins_datagrid():
            return render.DataGrid(filtered_data())


ui.hr()

with ui.layout_columns(fill=True):

    # Plotly Histogram Card
    with ui.card(full_screen=True):
        ui.h3("Plotly Histogram")

        @render_widget
        def histogram_plot():
            data = pd.DataFrame(filtered_data())
            attribute = attribute_reverse_map[input.selected_attribute()]

            # Validate data
            if not validate_data(data, attribute):
                return None  # Return nothing if data validation fails

            plotly_histogram = px.histogram(
                data_frame=data,
                x=attribute,
                nbins=input.plotly_bin_count(),
                color="species",
            ).update_layout(
                title={"text": f"{input.selected_attribute()} Frequency", "x": 0.5},
                yaxis_title="Count",
                xaxis_title=input.selected_attribute(),
            )
            return plotly_histogram

    # Plotly Scatter Plot Card
    with ui.card(full_screen=True):
        ui.h3("Plotly Scatter Plot")

        @render_widget
        def scatter_plot():
            data = pd.DataFrame(filtered_data())
            attribute = attribute_reverse_map[input.selected_attribute()]

            # Validate data
            if not validate_data(data, attribute):
                return None  # Return nothing if data validation fails

            plotly_scatterplot = px.scatter(
                data_frame=data, x=attribute, y="body_mass_g", color="species"
            ).update_layout(
                title={"text": f"{input.selected_attribute()} vs Body Mass(g)"},
                yaxis_title="Body Mass (g)",
                xaxis_title=input.selected_attribute(),
            )
            return plotly_scatterplot

    # Seaborn Histogram Card
    with ui.card(full_screen=True):
        ui.h3("Seaborn Histogram")

        @render.plot(
            alt="Seaborn histogram of the selected penguin attribute by species, with KDE overlay."
        )
        def seaborn_histogram():
            data = pd.DataFrame(filtered_data())
            attribute = attribute_reverse_map[input.selected_attribute()]

            # Validate data
            if not validate_data(data, attribute):
                return None  # Return nothing if data validation fails

            ax = sns.histplot(
                data=data,
                x=attribute,
                bins=input.seaborn_bin_count(),
                hue="species",
                element="step",
                kde=True,
            )
            ax.set_title(f"Distribution of {input.selected_attribute()} by Species")
            ax.set_xlabel(input.selected_attribute())
            ax.set_ylabel("Count")
            return ax
