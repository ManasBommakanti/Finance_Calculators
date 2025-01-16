#!/bin/bash

INCOME_TAX_CALC_DIR="Income_Tax_Calculator"
BUDGET_CALC_DIR="Budget_Calculator"

chmod +x "$INCOME_TAX_CALC_DIR/income_tax_calculator.py"
chmod +x "$BUDGET_CALC_DIR/budget_calculator.py"

# Would you like to plot income tax graph?
read -p "Would you like to plot income tax graph? (y/n): " plot_income_tax_graph
if [ "$plot_income_tax_graph" != "n" -a "$plot_income_tax_graph" != "y" ]; then
    echo "Improper input: use 'y' or 'n'"
    exit
fi

read -p "Enter your income (write 'n' if you would like to use config.json): " income
read -p "Enter the amount you would like to put into 401k (write 'n' if you would like to use config.json): " individ_401k_contrib
read -p "Enter the amount of remaining pre-tax deductions (write 'n' if you would like to use config.json): " pre_tax_deduct

tax_execute_string="$INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json"
if [ "$plot_income_tax_graph" == "y" ]; then
    tax_execute_string="$tax_execute_string -p"
fi
if [ "$income" != "n" ]; then
    tax_execute_string="$tax_execute_string -i $income"
fi
if [ "$individ_401k_contrib" != "n" ]; then
    tax_execute_string="$tax_execute_string -c $individ_401k_contrib"
fi
if [ "$pre_tax_deduct" != "n" ]; then
    tax_execute_string="$tax_execute_string -d $pre_tax_deduct"
fi

python $tax_execute_string

tax_execute_string="${tax_execute_string// -p/} -t"
effective_tax_rate=$(python $tax_execute_string)

printf "\nEffective tax rate: %.2f%% \n\n" $effective_tax_rate

# Would you also like to calculate budget?
read -p "Would you also like to calculate budget? (y/n): " calculate_budget

if [ "$calculate_budget" == "n" ]; then
    exit
fi

# Would you like to plot the graph of budget?
read -p "Would you like to plot the graph of budget? (y/n): " plot_graph

budget_execute_string="$BUDGET_CALC_DIR/budget_calculator.py $BUDGET_CALC_DIR/config.json -t $effective_tax_rate"

if [ "$plot_graph" == "y" ]; then
    budget_execute_string="$budget_execute_string -p"
fi
if [ "$income" != "n" ]; then
    budget_execute_string="$budget_execute_string -i $income"
fi
if [ "$individ_401k_contrib" != "n" ]; then
    budget_execute_string="$budget_execute_string -c $individ_401k_contrib"
fi
if [ "$pre_tax_deduct" != "n" ]; then
    budget_execute_string="$budget_execute_string -d $pre_tax_deduct"
fi

python $budget_execute_string