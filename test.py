import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

# Simple test plot
plt.plot([1, 2, 3], [1, 4, 9])
plt.title('Test Plot')

# Save the plot
try:
    plt.savefig('static/test_plot.png')
    print("Test plot saved successfully.")
except Exception as e:
    print(f"Error saving test plot: {e}")