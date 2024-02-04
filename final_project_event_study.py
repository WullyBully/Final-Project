import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Initialize today's date for use in downloading stock data.
today = datetime.date.today().strftime("%Y-%m-%d")

## Download stock data.
# META stock data.
meta_data = yf.download('META', start="2018-01-01", end="2023-08-31")
meta_data['Daily Returns'] = meta_data['Adj Close'].pct_change()
meta_data = meta_data.dropna()

# AMZN stock data.
amazon_data = yf.download('AMZN', start="2022-01-01", end=today)
amazon_data['Daily Returns'] = amazon_data['Adj Close'].pct_change()
amazon_data = amazon_data.dropna()

# IRBT stock data.
irbt_data = yf.download('IRBT', start="2022-01-01", end=today)
irbt_data['Daily Returns'] = irbt_data['Adj Close'].pct_change()
irbt_data = irbt_data.dropna()


# Normalize the data
meta_data['Normalized Returns'] = meta_data['Adj Close'] / meta_data.iloc[0]['Adj Close'] - 1
amazon_data['Normalized Returns'] = amazon_data['Adj Close'] / amazon_data.iloc[0]['Adj Close'] - 1
irbt_data['Normalized Returns'] = irbt_data['Adj Close'] / irbt_data.iloc[0]['Adj Close'] - 1

def plot_returns(data, column, title, filename, events):
    plt.figure(figsize=(12, 8))
    plt.plot(data.index, data[column], color='lightblue', linewidth=1)
    plt.xlabel('Date')
    plt.ylabel('Returns (in %)')
    plt.title(title)
    plt.grid(True)

    for event, (date, color) in events.items():
        event_date = pd.to_datetime(date)
        event_return = data.loc[event_date, column]
        plt.annotate(event, xy=(event_date, event_return), xytext=(event_date, event_return+0.02),
                     arrowprops=dict(arrowstyle='wedge', color=color), color=color, ha='right', va='bottom')

    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=event, markerfacecolor=color, markersize=8)
                       for event, (_, color) in events.items()]
    plt.legend(handles=legend_elements, loc='upper left')

    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

events_meta = {
    'Threads Launch': ('2023-07-05', 'r'),
    'Twitter Threatens Legal Action Over Threads': ('2023-07-06', 'g'),
    'Meta Cuts 11,000 Jobs': ('2022-11-09', '#FF69B4'),
    'Meta Threatens to Remove News': ('2022-12-05', 'm'),
    'Facebook Changes to Meta': ('2021-10-28', 'y'),
    'Zuckerberg Testifies to Congress': ('2018-04-10', 'c'),
    'Zuckerberg Appears on the Joe Rogan Podcast': ('2022-08-25', 'k'),
    'Zuckerberg Testifies Over Libra Crypto': ('2019-10-23', 'b'),
}

events_amazon = {'Amazon/IRBT Acquisition Announced - $61/Share': ('2022-08-05', 'r'),
                 'Merge Price Modfied to $51.75/Share': ('2023-07-25', 'g'),
                 'EU Antitrust Investigation Announced': ('2023-07-06', 'b'),
                 'EU Expected to Approve Acquisition '
                 '(Adjusted for Thanksgiving)': ('2023-11-24', 'm'),
                 'EU Unexpectedly Opposes Acquisition': ('2023-11-27', 'r'),
                 'Amazon/IRBT Acquisition Terminated': ('2024-01-29', 'g'),
}

events_irbt = {'Amazon/IRBT Acquisition Announced - $61/Share': ('2022-08-05', 'r'),
               'Merge Price Modfied to $51.75/Share': ('2023-07-25', 'g'),
               'EU Antitrust Investigation Announced': ('2023-07-06', 'b'),
                 'EU Expected to Approve Acquisition'
                 '(Adjusted for Thanksgiving)': ('2023-11-24', 'm'),
                 'EU Unexpectedly Opposes Acquisition': ('2023-11-27', 'r'),
                 'Amazon/IRBT Acquisition Terminated': ('2024-01-29', 'g'),
}

plot_returns(meta_data, 'Normalized Returns', 'Normalized Returns of Meta', 'meta_normalized_returns.png', events_meta)
plot_returns(meta_data, 'Daily Returns', 'Daily Returns for Meta', 'META_Daily_Returns_w_Events.png', events_meta)
plot_returns(amazon_data, 'Normalized Returns', 'Normalized Returns of AMZN', 'amzn_normalized_returns.png', events_amazon)
plot_returns(amazon_data, 'Daily Returns', 'Daily Returns for AMZN', 'AMZN_Daily_Returns_w_Events.png', events_amazon)
plot_returns(irbt_data, 'Normalized Returns', 'Normalized Returns of IRBT', 'irbt_normalized_returns.png', events_irbt)
plot_returns(irbt_data, 'Daily Returns', 'Daily Returns for IRBT', 'IRBT_Daily_Returns_w_Events.png', events_irbt)

########## Problem 1 part B. Event Study ##########

def event_study(stock_symbol, mkt_symbol, bef_event, aft_event, window_offset, window_size, events):
    if events:
        wofl = float(window_offset)
        wsfl = float(window_size)
        tot_days_before = round(1.8*(wofl + wsfl),0)
        tot_days_beforedat = tot_days_before + 10

        beffl = float(bef_event)
        aftfl = float(aft_event)

        events = {event: pd.to_datetime(date) for event, date in events.items()}

        for event, event_date in events.items():
            start_date = event_date - pd.DateOffset(days = tot_days_beforedat)
            end_date = event_date + pd.DateOffset(days = aftfl)

            mkt_data = yf.download(mkt_symbol, start=start_date, end=end_date, progress=False)
            stock_data = yf.download(stock_symbol, start=start_date, end=end_date, progress=False)

            stock_returns = stock_data['Adj Close'].pct_change()
            mkt_returns = mkt_data['Adj Close'].pct_change()

            event_window_start = event_date - pd.DateOffset(days = beffl)
            event_window_end = event_date + pd.DateOffset(days = aftfl)
            est_window_start = event_window_start - pd.DateOffset(days = tot_days_before)
            est_window_end = event_window_start - pd.DateOffset(days = wofl)

            print(f'\n########## {event} ##########\n'
                f'Start date: {est_window_start}', f'End date: {est_window_end}')

            estimation_window_stock = stock_returns[(stock_returns.index >= est_window_start) 
                                            & (stock_returns.index < est_window_end)]
            estimation_window_mkt = mkt_returns[(mkt_returns.index >= est_window_start) 
                                            & (mkt_returns.index < est_window_end)]
            
            varstock = np.var(estimation_window_stock)
            std_stk = np.sqrt(varstock)
            varmkt = np.var(estimation_window_mkt)
            std_mkt = np.sqrt(varmkt)
            correlation_matrix = np.corrcoef(estimation_window_stock, estimation_window_mkt)
            correlation = correlation_matrix[0,1]
            covar = correlation*std_mkt*std_stk
            beta = covar/varmkt
            print(f"\nBeta for event window is {round(beta, 4)}.\n")

            event_window_stock = stock_returns[(stock_returns.index >= event_window_start) & (stock_returns.index <= event_window_end)]
            event_window_mkt = mkt_returns[(mkt_returns.index >= event_window_start) & (mkt_returns.index <= event_window_end)]
            expected_returns = beta*event_window_mkt

            print(f"Expected Returns\n{expected_returns}\nStock During Window\n{event_window_stock}\n")

            abnormal_returns = event_window_stock - expected_returns

            CAR = abnormal_returns.sum()

            AAR = CAR/len(abnormal_returns)
            print(f"Cumulative Abnormal Return: {CAR}\n"
                f"Average Abnormal Return: {AAR}\nBeta: {round(beta, 4)}")
            print(f"Estimation Window: {len(estimation_window_stock)} |"
                f" Event Window: {len(event_window_stock)}\n")

            ARsq = np.square(abnormal_returns)
            varAR = 1/(len(estimation_window_stock)-1)*ARsq.sum()
            stdAR = np.sqrt(varAR)

            tAR = abnormal_returns/stdAR

            L2 = len(event_window_stock)
            varCAR = L2*varAR
            stdCAR = np.sqrt(varCAR)

            tCAR = CAR/stdCAR
            print(len(estimation_window_stock))

            print(f"Abnormal Returns:\n{abnormal_returns}"
                  f"\nT-Stats Abnomral returns: {round(tAR, 4)} | "
                  f"\nCumulative Abnormal Returns: {round(tCAR, 4)} | "
                  f"Standard Deviation for Abnormal Returns: {round(stdAR, 4)}\n")

            # I originally saved the dataframes as csv to make sure everything
            # formatted correctly. I left the code in here in just in case.
            # safe_event_name = ''.join(c if c.isalnum() else '_' for c in event)
            # mkt_data.to_csv(f'{safe_event_name}_mkt.csv')
            # stock_data.to_csv(f'{safe_event_name}_stock.csv')
        else:
            print("No more events to analyze.")

# Call the function
events_meta = {
    'Threads Launch': '2023-07-05',
    'Twitter Threatens Legal Action Over Threads': '2023-07-06',
    'Meta Cuts 11,000 Jobs': '2022-11-09',
    'Meta Threatens to Remove News': '2022-12-05',
    'Facebook Changes to Meta': '2021-10-28',
    'Zuckerberg Testifies to Congress': '2018-04-10',
    'Zuckerberg Appears on the Joe Rogan Podcast': '2022-08-25',
    'Zuckerberg Testifies Over Libra Crypto': '2019-10-23',
    }

events_amazon = {'Amazon - IRBT Merger Announced': '2022-08-05',
}

events_irbt = {'IRBT - Amazon Merger Announced': '2022-08-05',
               'IRBT - Amazon Merger Cancelled': '2024-01-29',
}

event_study('META', '^GSPC', 5, 5, 30, 180, events_meta)
event_study('AMZN', '^GSPC', 5, 5, 30, 180, events_amazon)
event_study('IRBT', '^GSPC', 5, 5, 30, 180, events_irbt)

