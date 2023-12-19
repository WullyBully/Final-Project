import numpy as np
import matplotlib.pyplot as plt

def calculate_share_price(fcfs, shares_outstanding, debt, cash, growth_rate, wacc):
    # Calculate the terminal value using the last cash flow
    terminal_value = fcfs[-1] / (wacc - growth_rate)

    # Initialize v0
    v0 = 0

    # Loop over each cash flow and add its discounted value to v0
    for i, cf in enumerate(fcfs):
        if i == len(fcfs) - 2:  # If it's the last cash flow, add the terminal value
            discounted_value = (fcfs[-2] + terminal_value) / ((1 + wacc) ** (i + 1))
            v0 += discounted_value
            break
        else:  # Otherwise, just discount the cash flow
            discounted_value = cf / ((1 + wacc) ** (i + 1))
            v0 += discounted_value

    # Calculate the share price
    equity_value = (v0 - debt + cash)
    share_price = equity_value / shares_outstanding
    enterprise_value = v0
    return equity_value, share_price, enterprise_value

# Call the function with the provided inputs
fcfs = []
shares_outstanding = 27.865605
debt = 359.73
cash = 117.95
wacc = 0.111165

# Generate a range of growth rates
growth_rates = np.linspace(0.035, 0.045, 100)

# Calculate the share price for each growth rate
share_prices = [calculate_share_price(fcfs, shares_outstanding, debt, cash, growth_rate, wacc)[1] for growth_rate in growth_rates]

# Plot the share prices
plt.plot(growth_rates, share_prices)
plt.xlabel('Growth Rate')
plt.ylabel('Share Price')
plt.title('Share Price vs Growth Rate')
plt.show()