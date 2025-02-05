import pandas as pd
from utils import analysis_combiner
import numpy as np
from scipy.stats import sem  # If you'd rather compute SEM directly
from math import sqrt
from statsmodels.stats.proportion import proportion_confint
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects

# read final_dashboard_df.csv
fd = pd.read_csv("final_dashboard_df.csv")

# Filter the DataFrame for the "Escalation - Two Choice" domain
escalation_df = fd[fd['domain'] == 'Escalation - Two Choice']

# Pivot the DataFrame to have models on the x-axis and answers as columns
pivot_df = escalation_df.pivot(index='model', columns='answer', values='percentage').fillna(0)

# Plot the distribution of answers
pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8))

plt.xlabel('Model')
plt.ylabel('Percentage')
plt.title('Distribution of Answers for Escalation - Two Choice Domain')
plt.legend(title='Answer')
plt.show()
