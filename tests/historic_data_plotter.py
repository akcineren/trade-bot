import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("data_BTCUSDT_1m.csv")

# Plot closing prices
df["close"].plot()

# Add title and labels
plt.title("BTCUSDT 1m closing prices")
plt.xlabel("Time")
plt.ylabel("Price (USDT)")

plt.show()
