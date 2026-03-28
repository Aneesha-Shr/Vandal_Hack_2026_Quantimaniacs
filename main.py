import matplotlib.pyplot as plt
'''
rent = 0
house_cost = 0
int_rate = 0 #interest rate on loan
increase_home_val = 0 #percentage of increase in home value per year
increase_rent = 0 #percentage of rent increase per year
treasury_bond = 0 #return rate on a treasury bond per year
down_payment_percent = 0
loan_term_years = 0



def calculate_rent_total(mortgage_price):
   if mortgage_price > rent:
      diff = mortgage_price-rent
   else:
      diff = rent - mortgage_price
'''
def calculate_rent_vs_buy(
    house_cost, 
    rent, 
    int_rate, 
    increase_home_val, 
    increase_rent, 
    treasury_bond, 
    down_payment_percent, 
    loan_term_years
):
    # --- Initial Setup ---
    down_payment = house_cost * down_payment_percent
    loan_principal = house_cost - down_payment
    
    # Monthly rates for calculations
    monthly_int_rate = int_rate / 12
    total_payments = loan_term_years * 12
    
    # Standard Fixed-Rate Mortgage Formula
    if monthly_int_rate > 0:
        monthly_mortgage = loan_principal * (monthly_int_rate * (1 + monthly_int_rate)**total_payments) / ((1 + monthly_int_rate)**total_payments - 1)
    else:
        monthly_mortgage = loan_principal / total_payments

    # --- Tracking Variables ---
    current_home_value = house_cost
    current_loan_balance = loan_principal
    current_monthly_rent = rent
    
    # Renter starts with the down payment invested
    renter_capital = down_payment 
    
    # Lists to store yearly data for graphing
    years = list(range(1, loan_term_years + 1))
    buyer_equity_history = []
    renter_capital_history = []

    # --- The Simulation Loop ---
    for year in range(1, loan_term_years + 1):
        
        # 1. Buyer calculations (Monthly loop for accurate amortization)
        for _ in range(12):
            interest_payment = current_loan_balance * monthly_int_rate
            principal_payment = monthly_mortgage - interest_payment
            current_loan_balance -= principal_payment
            
        # Home value appreciates annually
        current_home_value *= (1 + increase_home_val)
        
        # Buyer Capital (Equity) = Asset Value - Remaining Debt
        buyer_equity = current_home_value - current_loan_balance
        buyer_equity_history.append(buyer_equity)
        
        # 2. Renter calculations
        yearly_mortgage_cost = monthly_mortgage * 12
        yearly_rent_cost = current_monthly_rent * 12
        
        # Difference in cash flow (Positive means renting is cheaper that year)
        cash_flow_difference = yearly_mortgage_cost - yearly_rent_cost
        
        # Renter's capital grows by the treasury bond rate, plus/minus the cash flow difference
        renter_capital = (renter_capital * (1 + treasury_bond)) + cash_flow_difference
        renter_capital_history.append(renter_capital)
        
        # Rent increases annually
        current_monthly_rent *= (1 + increase_rent)

    # --- Graphing the Results ---
    plt.figure(figsize=(10, 6))
    plt.plot(years, buyer_equity_history, label='Buyer Capital (Home Equity)', color='blue', linewidth=2)
    plt.plot(years, renter_capital_history, label='Renter Capital (Invested in Treasury)', color='orange', linewidth=2)
    
    plt.title('Rent vs. Buy: Capital Accumulation Over Time')
    plt.xlabel('Years')
    plt.ylabel('Total Capital ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# --- Example Execution ---
calculate_rent_vs_buy(
    house_cost=400000,          # $400,000 home
    rent=2000,                  # $1,000/month starting rent
    int_rate=0.065,             # 6.5% mortgage interest rate
    increase_home_val=0.03,     # 3% annual home appreciation
    increase_rent=0.04,         # 4% annual rent increase
    treasury_bond=0.04,         # 4.5% annual return on investment
    down_payment_percent=0.2, 
    loan_term_years=30
)