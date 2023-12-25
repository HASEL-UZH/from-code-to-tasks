import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.io as pio

from src.core.workspace_context import get_results_dir


INPUT_FILE = os.path.join(get_results_dir(), "foundation_analysis.csv")
OUTPUT_FILE_SVG = os.path.join(get_results_dir(), "foundation_analysis.svg")
OUTPUT_FILE_PNG = os.path.join(get_results_dir(), "foundation_analysis.png")
# Let"s assume you have a CSV file named "data.csv" with a column "count"
# Load your dataset into a Pandas DataFrame
df = pd.read_csv(INPUT_FILE)

# exclude the "summary"
df = df[df["type"] != "summary"]
df = df[df["technology"] == "NLTK"]

# Define the bin edges as if the counts were percentages (0 to 100)
bins = [x / 100.0 for x in range(0, 101)]  # creates a list [0, 0.01, 0.02, ..., 1.0]

if False:
    # Plot the histogram
    plt.hist(df["percentage"], bins=bins, edgecolor="white", color="tab:blue")  # Adjust the number of bins as needed

    # Add title and labels to the histogram
    plt.title("Histogram")
    plt.xlabel("Match percentage")
    plt.ylabel("Frequency")

    # Show the plot
    plt.show()

if True:

    # Let's assume you have a DataFrame 'df' with a column 'data_column' you want to plot.
    # For demonstration purposes, I'll create a simple DataFrame with random data.
    import pandas as pd
    import numpy as np

    # Create the histogram
    fig = px.histogram(df, x='percentage', nbins=10, title='Histogram of Data')
    fig.update_traces(marker=dict(line=dict(color='white', width=2)))
    fig.update_layout(bargap=0.2)  # 20% gap between bars
    fig.update_layout(xaxis_tickformat='.0%')  # use '.2%' for two decimals
    fig.update_xaxes(range=[-0.05, 1.05])
    fig.update_xaxes(nticks=20)

    # pio requires pip install -U kaleido
    pio.write_image(fig, OUTPUT_FILE_SVG, format='svg')
    pio.write_image(fig, OUTPUT_FILE_PNG, format='png', width=1600, height=900, scale=1)

    # Show the plot
    fig.show()

if True:
    # Create the histogram
    sns.histplot(df["percentage"], bins=10, kde=False, edgecolor="white", color="tab:blue")  # Adjust bins if needed
    # Add title and axis labels (Seaborn uses Matplotlib under the hood for this)
    plt.title("Histogram")
    plt.xlabel("Match percentage")
    plt.ylabel("Frequency")

    # Show the plot
    plt.show()


if True:
    # Calculate the number of zero and non-zero counts
    zero_count = (df["percentage"] == 0).sum()
    non_zero_count = (df["percentage"] != 0).sum()

    # Data to plot
    labels = "Zero percentage", "Others"
    sizes = [zero_count, non_zero_count]
    colors = ["tab:blue", "tab:orange"]
    explode = (0.1, 0)  # explode the 1st slice (zero counts)

    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return "{p:.1f}%".format(p=pct) if pct > 0 else ""
        return my_format

    # Plot the pie chart
    # plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=False, startangle=90, textprops={"color":"white"})
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            shadow=False, startangle=90,
            autopct=autopct_format(sizes),
            textprops={"color":"black"})

    wedges, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                                       shadow=False, startangle=90, autopct=autopct_format(sizes))

    # Set the percentage text color to white
    plt.setp(autotexts, **{"color":"white", "weight":"bold"})
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn a

    # Add title to the pie chart
    plt.title("Proportion of Zero vs Non-Zero percentages")

    # Show the plot
    plt.show()