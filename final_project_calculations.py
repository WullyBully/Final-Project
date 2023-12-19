import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

########## Problem 2 ##########
# Initialize the dataframes for the stock and market data.
irbt_data = yf.download('IRBT', start="2017-09-01", end="2022-08-31",
                        interval="1mo")
irbt_data['Daily Returns'] = irbt_data['Adj Close'].pct_change()
irbt_data.dropna()
mkt_data = yf.download('^GSPC', start="2017-09-01", end="2022-08-31",
                       interval="1mo")
mkt_data['Daily Returns'] = mkt_data['Adj Close'].pct_change() 
mkt_data.dropna()

## Answer some of the none calculation based questions.
# A) This is a cash aqcuisiton to be originally executed at $61/share, but was
# later modified to $51.75/share.



# Calculate the Equity cost of Capital for IRBT using the CAPM model.
def equity_cost_of_capital(ticker, rm, rf, start_date, end_date, interval):
    stock_data = yf.download(ticker, start=start_date, end=end_date,
                             interval=interval)
    stock_data['Daily Returns'] = stock_data['Adj Close'].pct_change()
    stock_data.dropna()
    mkt_data = yf.download('^GSPC', start=start_date, end=end_date,
                           interval=interval)
    mkt_data['Daily Returns'] = mkt_data['Adj Close'].pct_change() 
    mkt_data.dropna()
    mkt_var = mkt_data['Daily Returns'].var()
    stock_mkt_cov = stock_data['Daily Returns'].cov(mkt_data['Daily Returns'])
    stock_beta = stock_mkt_cov / mkt_var

    Re = rf + stock_beta * (rm - rf)
    return Re

cost_of_equity = equity_cost_of_capital('IRBT', 0.10, 0.0333, '2017-09-01',
                                        '2022-08-31', '1mo')
print(f"\nB. The equity cost of capital for IRBT is {cost_of_equity:.4%}")

## Calculate the WACC for IRBT.
# Cost of debt, from FactSet Key Stats
cost_of_debt = 0.0578

# Total equity and debt, in millions of dollars
equity_total = 1117.6
debt_total = 204.4

# Total capital, in millions of dollars
total_cap = 1322.0

# Calculate the WACC
wacc = (cost_of_equity * (equity_total / total_cap)) + (cost_of_debt * (debt_total / total_cap))
print(f"\nC. The WACC for IRBT is {wacc:.4%}")  # Different from Factset due to
                                                # their use of different rates.
                                                # Market Return = 5.00% and
                                                # risk free rate = 4.15%, and
                                                # a 3y beta of 0.77.

## Part D.
"""A function to calculate enterprise value, equity value, and share price."""
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

# Estimate free cash flows by average last two positives and growing at 5%.
dec_19 = 94.72
dec_20 = 200.45
dec_21_est = ((dec_19 + dec_20) / 2) * 1.05
dec_22_est = dec_21_est * 1.05
dec_23_est = dec_22_est * 1.05
dec_24_est = dec_23_est * 1.05
dec_25_est = dec_24_est * 1.05

# Set up the inputs for the share price function.
fcfs = [dec_23_est, dec_24_est, dec_25_est]
shares_outstanding = 27.865605
debt = 359.73
cash = 117.95

enterprise_val = calculate_share_price(fcfs, shares_outstanding, debt, cash,
                                        0.04, wacc)[2]
share_price = calculate_share_price(fcfs, shares_outstanding, debt, cash,
                                    0.04, wacc)[1]
print(f"\nPart D - A)\nThe present value of FCF for IRBT at 4% growth is"
      f" ${enterprise_val:.2f} million, with a share price of ${share_price:.2f}")

def plot_share_price_vs_growth_rate(title, fcfs, shares_outstanding, debt,
                                    cash, wacc, growth_rate_start,
                                    growth_rate_end, num_growth_rates, filename):
    import numpy as np
    import matplotlib.pyplot as plt

    # Generate a range of growth rates
    growth_rates = np.linspace(growth_rate_start, growth_rate_end,
                               num_growth_rates)

    # Calculate the share price for each growth rate
    share_prices = [calculate_share_price(fcfs, shares_outstanding,
                                          debt, cash, growth_rate, wacc)[1]
                                          for growth_rate in growth_rates]

    # Set the style of the plot to 'ggplot' for a more colorful and grid-lined plot
    plt.style.use('ggplot')

    # Create a new figure with a specific size
    plt.figure(figsize=(10, 6))

    # Plot the share prices with a thicker line and a different color
    plt.plot(growth_rates, share_prices, 'r-', linewidth=2.5)

    # Add labels and title with a larger font size
    plt.xlabel('Growth Rate', fontsize=14)
    plt.ylabel('Share Price', fontsize=14)
    plt.title(title, fontsize=16)

    # Increase the tick size for better visibility
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Add callouts for every tenth of a percent along the x-axis
    for i in range(len(growth_rates)):
        if i % 10 == 0:  # Every tenth of a percent
            plt.annotate(f'${share_prices[i]:,.2f}', (growth_rates[i],
                                                      share_prices[i]),
                                                      textcoords="offset points",
                                                      xytext=(-10,10), ha='center',
                                                      color='blue', weight='bold')

    # Save the plot
    plt.savefig(filename)

    # Show the plot
    plt.show()
title = 'IRBT: Share Price vs Growth Rate'
plot_share_price_vs_growth_rate(title, fcfs, shares_outstanding, debt, cash,
                                wacc, 0.035, 0.045, 100,
                                'share_price_vs_growth_rate.png')

def free_cash_flow(ebit, tax, depreciation, capex, change_wc):
    """Calculate free cash flow."""
    return ebit * (1 - tax) + depreciation - capex - change_wc

# All values in millions of dollars.
ebit2021 = 10.1
tax2021 = 0.2079
depreciation2021 = 33.3
capex2021 = -29.93
change_nwc2021 = -86.31

fcf = free_cash_flow(ebit2021, tax2021, depreciation2021, capex2021,
                     change_nwc2021)
print(f"\nD - B)\nThe free cash flow for IRBT is {fcf:.2f} million dollars.")

## Re-estimate the share price using financial statement data.
# Calculate future free cash flows based on 5% growth rate.
dec_21_reest = free_cash_flow(ebit2021, tax2021, depreciation2021, capex2021,
                              change_nwc2021)
dec_22_reest = dec_21_reest * 1.05
dec_23_reest = dec_22_reest * 1.05
dec_24_reest = dec_23_reest * 1.05
dec_25_reest = dec_24_reest * 1.05

# Re-calculate share price.
free_cash_flows_est = [dec_23_reest, dec_24_reest, dec_25_reest]
shares_outstanding = 27.865605
debt = 359.73
cash = 117.95
share_price_reest = calculate_share_price(free_cash_flows_est,
                                          shares_outstanding,
                                          debt, cash, 0.04,wacc)[1]
print(f"The re-estimated share price for IRBT at 4% growth is"
      f" ${share_price_reest:.2f}")

# Re-plot the new estimated share price.
title_rest = 'Re-Estimated IRBT: Share Price vs Growth Rate'
plot_share_price_vs_growth_rate(title_rest, free_cash_flows_est, 
                                shares_outstanding, debt, cash, wacc, 
                                0.035, 0.045, 100,
                                'reest_share_price_vs_growth_rate_reest.png')