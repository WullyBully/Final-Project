def free_cash_flow(ebit, tax, depreciation, capex, change_wc):
    """Calculate free cash flow."""
    return ebit * (1 - tax) + depreciation - capex - change_wc

# All values in millions of dollars.
ebit2021 = 10.1
tax2021 = 0.2079
depreciation2021 = 33.3
capex2021 = 29.93
change_nwc2021 = 86.31

fcf = free_cash_flow(ebit2021, tax2021, depreciation2021, capex2021, change_nwc2021)
print(f"\nD. The free cash flow for IRBT is {fcf:.2f} million dollars.")