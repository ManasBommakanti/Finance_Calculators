import sys, json
import plotly.graph_objects as go

# Usage: python budget_calculator.py <config_file> [-t <tax_rate>] [-p (plot)] [-i <income>] [-c <401k_contribution>] [-d <pre_tax_deducts>] [-b <post_tax_bonus>]


def plot_budget_pie_chart(info, expenses):
    # Extract relevant data from the dictionary
    income = info["Income"]["Net Salary (minus all deductions)"]
    retirement = (info["Retirement"]["401k Contribution (Individual)"]) / income
    # expenses = info["Expenses"]["Monthly Expenses"] * 12
    expenses_cleaned = {
        key: (value * 12) / income for key, value in expenses.items() if value > 0
    }
    emergency_fund = info["Emergency Fund"]["Emergency Fund Per Month"] * 12 / income
    additional_savings = (
        info["Additional Savings"]["Savings Per Month"] * 12
        + info["Retirement"]["Roth IRA Contribution"]
    ) / income
    leftover = (
        info["Income"]["Post-Tax Salary"] - info["Summary"]["Accumulated Spending"]
    ) / income

    # Labels and values for the pie chart
    labels = [
        "Retirement Contributions",
        "Emergency Fund",
        "Additional Savings",
        "Leftover",
        *expenses_cleaned.keys(),
    ]
    values = [
        retirement,
        emergency_fund,
        additional_savings,
        leftover,
        *expenses_cleaned.values(),
    ]

    # Create the pie chart
    # plt.figure(figsize=(8, 8))
    # plt.pie(
    #     values,
    #     labels=labels,
    #     autopct="%1.1f%%",  # Add percentages
    #     startangle=140,
    #     colors=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    # )

    # # Add a title
    # plt.title("Annual Budget Breakdown")
    # plt.axis("equal")  # Equal aspect ratio ensures the pie chart is a circle
    # plt.show()

    # Create the interactive pie chart
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hoverinfo="label+percent",  # Show label and percentage on hover
                textinfo="none",  # Hide labels by default
                marker=dict(
                    colors=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
                ),
            )
        ]
    )

    # Update layout for title and styling
    fig.update_layout(
        title_text="Annual Budget Breakdown",
        title_x=0.5,  # Center-align title
        showlegend=True,  # Remove legend as labels are displayed on hover
    )

    # Display the interactive chart
    fig.show()


def calculate(
    base_salary,
    tax_rate,
    post_tax_bonus,
    max_401k_contribution,
    max_roth_ira_contribution,
    expenses,
    employer_match_percentage,
    misc,
    paycheck_frequency=26,
):
    """
    Calculate post-tax, post-401k paycheck and total annual savings based on user inputs.

    Parameters:
        base_salary (float): Annual base salary in USD.
        tax_rate (float): Total tax rate (Federal + State + FICA) as a percentage (e.g., 27.96%).
        post_tax_bonus (float): Post-tax bonus amount in USD.
        max_401k_contribution (float): Maximum allowable individual 401k contribution.
        max_roth_ira_contribution (float): Maximum allowable Roth IRA contribution.
        expenses (dict): Dictionary containing monthly expenses (rent, insurance, etc.).
        employer_match_percentage (list(tuple(float, float))): Employer's 401k match percentages
        misc (dict): Miscellaneous information including emergency fund and savings rate.
        paycheck_frequency (int): Number of pay periods in a year (default is 26 for biweekly).

    Returns:
        dict: A dictionary containing detailed calculations.
    """

    # Extract miscellaneous information
    savings_rate = misc["savings_rate"]
    emergency_fund_months = misc["emergency_fund_months"]
    emergency_fund_payoff_months = misc["emergency_fund_payoff_months"]
    stock = misc["stock"]
    stock_matching = misc["stock_matching"]
    pre_tax_deducts = misc["pre-tax deductions"]

    # Calculate gross paycheck
    gross_paycheck = base_salary / paycheck_frequency

    # 401k Contributions
    individual_401k_per_paycheck = (
        max_401k_contribution / paycheck_frequency
    )  ### IMPORTANT

    total_employer_match = 0
    for match_percentage, match_duration in employer_match_percentage:
        total_employer_match += base_salary * (match_percentage / 100) * match_duration

    total_401k_contribution = max_401k_contribution + total_employer_match

    post_401k_salary = base_salary - max_401k_contribution - pre_tax_deducts

    # Taxes and deductions
    annual_tax = base_salary * (tax_rate / 100)
    post_tax_salary = post_401k_salary - annual_tax
    post_tax_paycheck = post_tax_salary / paycheck_frequency

    # Calculate post-stock salary and paycheck after 401k reduction
    stock_contribution = base_salary * stock
    company_contribution = stock_contribution * stock_matching
    post_stock_bonus_salary = post_tax_salary + (
        company_contribution * (1 - (tax_rate / 100))
    )
    post_stock_bonus_paycheck = post_stock_bonus_salary / paycheck_frequency

    # Calculate salary after post-tax bonus
    post_stock_bonus_salary += post_tax_bonus
    post_stock_bonus_paycheck += post_tax_bonus / paycheck_frequency

    # Calculate Roth IRA contribution
    roth_ira_per_paycheck = max_roth_ira_contribution / paycheck_frequency
    roth_ira_per_month = max_roth_ira_contribution / 12

    # Net paycheck after Roth IRA contributions
    net_annual_salary = post_stock_bonus_salary - max_roth_ira_contribution
    net_paycheck = net_annual_salary / paycheck_frequency

    # Monthly expenses
    total_monthly_expenses = float(sum(expenses.values()))
    total_monthly_expenses_paycheck = (
        total_monthly_expenses * 12
    ) / paycheck_frequency  ### IMPORTANT

    # Calculate additional savings from paycheck based on savings rate
    additional_savings_per_paycheck = net_paycheck * (savings_rate)  ### IMPORTANT
    additional_savings_per_month = additional_savings_per_paycheck * (
        paycheck_frequency / 12
    )

    # Calculate the required emergency fund to cover the specified number of months
    required_emergency_fund = total_monthly_expenses * emergency_fund_months

    # Calculate the monthly contribution needed to achieve the required emergency fund in the specified months
    emergency_fund_per_month = 0.0
    if emergency_fund_payoff_months > 0:
        emergency_fund_per_month = (
            required_emergency_fund / emergency_fund_payoff_months
        )
    emergency_fund_per_paycheck = emergency_fund_per_month / (paycheck_frequency / 12)

    balance = paycheck_frequency * (
        individual_401k_per_paycheck
        + roth_ira_per_paycheck
        + total_monthly_expenses_paycheck
        + emergency_fund_per_paycheck
        + additional_savings_per_paycheck
    )

    return {
        "Income": {
            "Base Salary": base_salary,
            "Gross Paycheck": gross_paycheck,
            "Post-Tax Salary": post_tax_salary,
            "Post-Tax Paycheck": post_tax_paycheck,
            "Post-Stock and Post-Tax Bonus Salary": post_stock_bonus_salary,
            "Post-Stock and Post-Tax Bonus Paycheck": post_stock_bonus_paycheck,
            "Net Salary (minus all deductions)": net_annual_salary,
            "Net Paycheck (minus all deductions)": net_paycheck,
        },
        "Stock": {
            "Stock Contribution": stock_contribution,
            "Company Contribution": company_contribution,
            "Total Contribution": stock_contribution + company_contribution,
        },
        "Retirement": {
            "401k Contribution (Individual)": max_401k_contribution,
            "Employer Match": total_employer_match,
            "Total 401k Contribution": total_401k_contribution,
            "Individual 401k Contribution Per Paycheck": individual_401k_per_paycheck,
            "Roth IRA Contribution": max_roth_ira_contribution,
            "Roth IRA Contribution Per Month": roth_ira_per_month,
            "Roth IRA Contribution Per Paycheck": roth_ira_per_paycheck,
        },
        "Expenses": {
            "Monthly Expenses Per Paycheck": total_monthly_expenses_paycheck,
            "Monthly Expenses": total_monthly_expenses,
        },
        "Emergency Fund": {
            "Required Emergency Fund": required_emergency_fund,
            "Emergency Fund Per Paycheck": emergency_fund_per_paycheck,
            "Emergency Fund Per Month": emergency_fund_per_month,
        },
        "Additional Savings": {
            "Savings Per Paycheck": additional_savings_per_paycheck,
            "Savings Per Month": additional_savings_per_month,
        },
        "Summary": {
            "Accumulated Spending": balance,
            "Pass": balance < net_annual_salary,
            "advice": (
                "Everything is balanced."
                if balance == net_annual_salary
                else (
                    f"You are using ${balance - net_annual_salary:,.2f} more than you have! We need to save more. "
                    f"This is ${balance / paycheck_frequency - net_paycheck:,.2f} over per paycheck."
                    if balance > net_annual_salary
                    else f"You are saving ${net_annual_salary - balance:,.2f} less than you need! There is still more room to spend. "
                    f"This is saving ${net_paycheck - balance / paycheck_frequency:,.2f} per paycheck."
                )
            ),
        },
    }


def run():
    if len(sys.argv) < 2:
        print(
            "Usage: python budget_calculator.py <config_file> [-t <tax_rate>] [-p (plot)] [-i <income>] [-c <401k_contribution>] [-d <pre_tax_deducts>] [-b <post_tax_bonus>]"
        )
        sys.exit(1)

    # Load the JSON file
    with open(sys.argv[1], "r") as file:
        config = json.load(file)

    # Access income section
    income = config["income"]
    base_salary = (
        float(sys.argv[sys.argv.index("-i") + 1])
        if "-i" in sys.argv
        else float(income["base_salary"])
    )
    tax_rate = (
        float(sys.argv[sys.argv.index("-t") + 1])
        if "-t" in sys.argv
        else float(income["tax_rate"])
    )
    paycheck_frequency = income["paycheck_frequency"]
    post_tax_bonus = (
        float(sys.argv[sys.argv.index("-b") + 1])
        if "-b" in sys.argv
        else income["post_tax_bonus"]
    )

    # Access expenses section
    expenses = config["expenses"]

    # Access retirement section
    retirement = config["retirement"]
    max_401k_contribution = (
        float(sys.argv[sys.argv.index("-c") + 1])
        if "-c" in sys.argv
        else retirement["max_401k_contribution"]
    )
    max_roth_ira_contribution = retirement["max_roth_ira_contribution"]
    employer_match_percentage = retirement["employer_match_percentage"]

    # Access misc section
    misc = config["misc"]

    misc["pre-tax deductions"] = (
        float(sys.argv[sys.argv.index("-d") + 1])
        if "-d" in sys.argv
        else float(misc["pre-tax deductions"])
    )

    print()
    print("INPUTS")
    print("------")

    # Print the inputs in a structured format
    print(f"Base Salary: ${base_salary:,.2f}")
    print(f"Tax Rate: {tax_rate}%")
    print(f"Paycheck Frequency: {paycheck_frequency} paychecks per year")
    print("Expenses:")
    for category, amount in expenses.items():
        print(f"  - {category}: ${amount:,.2f}")

    print(f"Max 401k Contribution: ${max_401k_contribution:,.2f}")
    print("Employer Match Percentages:")
    for match_percentage, match_duration in employer_match_percentage:
        print(f"  - {match_percentage}% for {match_duration}")

    print("Miscellaneous:")
    for key, value in misc.items():
        if key == "emergency_fund":
            print(f"  - {key}: ${value:,.2f}")
        else:
            print(f"  - {key}: {value}")

    info = calculate(
        base_salary=float(base_salary),
        post_tax_bonus=float(post_tax_bonus),
        tax_rate=float(tax_rate),
        max_401k_contribution=float(max_401k_contribution),
        max_roth_ira_contribution=float(max_roth_ira_contribution),
        expenses=expenses,
        employer_match_percentage=employer_match_percentage,
        misc=misc,
        paycheck_frequency=paycheck_frequency,
    )

    print()
    print("RESULTS")
    print(("-------"))

    max_key_length = max(
        len(key)
        for details in info.values()
        for key in details.keys()
        if key != "advice"
    )

    plot = False

    # Print the results in a structured format
    for category, details in info.items():
        print(f"{category}:")
        for key, value in details.items():
            if category == "Summary":
                if key == "Pass":
                    plot = bool(value)
                elif key == "advice":
                    print()
                    print(value)
                else:
                    print(f"  - {key.ljust(max_key_length)} : ${value:,.2f}")
            else:
                # Format the keys and values into a single column
                if isinstance(value, float):
                    print(f"  - {key.ljust(max_key_length)} : ${value:,.2f}")
                else:
                    print(f"  - {key.ljust(max_key_length)} : {value}")
        print()  # Add a blank line for better readability

    if plot and "-p" not in sys.argv:
        plot = False

    if plot:
        plot_budget_pie_chart(info, expenses)


if __name__ == "__main__":
    run()
