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

# Calculate income tax
if [ "$plot_income_tax_graph" == "y" ]; then
    if [ "$income" == "n" ]; then
        python $INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json -p
    else
        python $INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json -i $income -p
    fi
elif [ "$plot_income_tax_graph" == "n" -a "$income" != "n" ]; then
    python $INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json -i $income
fi

if [ "$income" == "n" ]; then
    effective_tax_rate=$(python $INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json -t)
else
    effective_tax_rate=$(python $INCOME_TAX_CALC_DIR/income_tax_calculator.py $INCOME_TAX_CALC_DIR/config.json -t -i $income)
fi

printf "\nEffective tax rate: %.2f%% \n\n" $effective_tax_rate

# Would you also like to calculate budget?
read -p "Would you also like to calculate budget? (y/n): " calculate_budget

if [ "$calculate_budget" == "n" ]; then
    exit
fi

# Would you like to plot the graph of budget?
read -p "Would you like to plot the graph of budget? (y/n): " plot_graph

# Calculate budget
if [ "$plot_graph" == "y" ]; then
    if [ $income == "n" ]; then
        python $BUDGET_CALC_DIR/budget_calculator.py $BUDGET_CALC_DIR/config.json -t $effective_tax_rate -p
    else
        python $BUDGET_CALC_DIR/budget_calculator.py $BUDGET_CALC_DIR/config.json -t $effective_tax_rate -p -i $income
    fi
else
    if [ $income == "n" ]; then
        python $BUDGET_CALC_DIR/budget_calculator.py $BUDGET_CALC_DIR/config.json -t $effective_tax_rate
    else
        python $BUDGET_CALC_DIR/budget_calculator.py $BUDGET_CALC_DIR/config.json -t $effective_tax_rate -i $income
    fi
fi