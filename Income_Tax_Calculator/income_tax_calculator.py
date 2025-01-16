import sys, json
import plotly.graph_objects as go

# Usage: python income_tax_calculator.py <config_file> [-t (only tax)] [-p (plot)] [-i income] [-c (401k contribution)] [-d pre_tax_deducts]


def plot_tax(tax, net_income):
    labels = list(tax.keys())[0:-2] + ["Net Income"]
    values = [tax[key]["amount"] for key in labels[0:-1]] + [net_income]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.show()


def calculate_tax(
    gross_income, pre_tax_deducts, federal_bracket, state_bracket, local_bracket, fica
):
    gross_income -= pre_tax_deducts
    federal_tax, effective_fed_tax = calculate_bracket_tax(
        gross_income, federal_bracket
    )
    state_tax, effective_state_tax = calculate_bracket_tax(gross_income, state_bracket)
    local_tax, effective_local_tax = calculate_bracket_tax(gross_income, local_bracket)
    fica_tax, effectice_fica_tax = calculate_fica_tax(gross_income, fica)
    total_tax = federal_tax + state_tax + local_tax + fica_tax
    total_effective_tax = (
        effective_fed_tax
        + effective_state_tax
        + effective_local_tax
        + effectice_fica_tax
    )

    return {
        "Federal Tax": {
            "amount": federal_tax,
            "effective_rate": effective_fed_tax,
        },
        "State Tax": {
            "amount": state_tax,
            "effective_rate": effective_state_tax,
        },
        "Local Tax": {
            "amount": local_tax,
            "effective_rate": effective_local_tax,
        },
        "FICA Tax": {
            "amount": fica_tax,
            "effective_rate": effectice_fica_tax,
        },
        "Summary": {
            "amount": total_tax,
            "effective_rate": total_effective_tax,
        },
        "Net Income": gross_income - total_tax,
    }


def calculate_bracket_tax(gross_income, bracket):
    if bracket is None or bracket == []:
        return 0, 0

    total_tax = 0.0

    for i in range(1, len(bracket)):
        if gross_income > bracket[i][1]:
            total_tax += (bracket[i][1] - bracket[i - 1][1]) * bracket[i][0] / 100
        else:
            total_tax += (
                (gross_income - bracket[i - 1][1]) * bracket[i][0] / 100
                if gross_income > bracket[i - 1][1]
                else 0
            )
            break

    return total_tax, float(total_tax) / gross_income * 100


def calculate_fica_tax(gross_income, fica):
    return gross_income * fica / 100, fica


def run():
    if len(sys.argv) < 2:
        print(
            "Usage: python income_tax_calculator.py <config_file> [-t (only tax)] [-p (plot)] [-i income] [-c (401k contribution)] [-d pre_tax_deducts]"
        )
        return

    with open(sys.argv[1]) as f:
        config = json.load(f)

    gross_income = (
        float(sys.argv[sys.argv.index("-i") + 1])
        if "-i" in sys.argv
        else config["gross_income"]
    )
    individual_401k_contribution = (
        float(sys.argv[sys.argv.index("-c") + 1])
        if "-c" in sys.argv
        else config["401k contribution"]
    )
    pre_tax_deduct = (
        float(sys.argv[sys.argv.index("-d") + 1])
        if "-d" in sys.argv
        else config["pre-tax deductions"]
    )
    federal_bracket = config["federal_bracket"]
    state_bracket = config["state_bracket"]
    local_bracket = config["local_bracket"]
    fica = config["fica"]

    tax = calculate_tax(
        gross_income,
        individual_401k_contribution + pre_tax_deduct,
        federal_bracket,
        state_bracket,
        local_bracket,
        fica,
    )

    if "-t" in sys.argv:
        print(tax["Summary"]["effective_rate"])
        return

    print()
    for key, value in tax.items():
        if key != "Net Income":
            print(f"{key}: ${value['amount']:,.2f} ({value['effective_rate']:.2f}%)")
        else:
            print(f"{key}: ${value:,.2f}")
    print()

    (
        plot_tax(tax, gross_income - tax["Summary"]["amount"])
        if "-p" in sys.argv
        else None
    )


if __name__ == "__main__":
    run()
