import sys, json
import plotly.graph_objects as go

# Usage: python budget_calculator.py <config_file> [-b bonus_amount] [-p (plot)] [-o (print only bonus)]


def plot_bonus(bonus, federal_tax, state_tax, local_tax, fica):
    labels = ["Federal Tax", "State Tax", "Local Tax", "FICA", "Net Bonus"]
    values = [
        bonus * federal_tax,
        bonus * state_tax,
        bonus * local_tax,
        bonus * fica,
        bonus * (1 - federal_tax - state_tax - local_tax - fica),
    ]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
    fig.update_layout(title_text="Bonus Distribution")
    fig.show()


def calculate_bonus_post_tax(bonus, federal_tax, state_tax, local_tax, fica):
    net_bonus = bonus * (1 - federal_tax - state_tax - local_tax - fica)
    return {
        "Initial Bonus": bonus,
        "Federal Tax": bonus * federal_tax,
        "State Tax": bonus * state_tax,
        "Local Tax": bonus * local_tax,
        "FICA": bonus * fica,
        "Net Bonus": net_bonus,
    }


def run():
    if len(sys.argv) < 2:
        print(
            "Usage: python bonus_calculator.py <config_file> [-b bonus_amount] [-p (plot)] [-o (print only bonus)]"
        )
        sys.exit(1)

    # Load the JSON file
    with open(sys.argv[1], "r") as file:
        config = json.load(file)

    bonus = (
        float(sys.argv[sys.argv.index("-b") + 1])
        if "-b" in sys.argv
        else config["bonus"]
    )
    federal_tax = config["federal_tax_rate"]
    state_tax = config["state_tax_rate"]
    local_tax = config["local_tax_rate"]
    fica = config["fica"]

    info = calculate_bonus_post_tax(bonus, federal_tax, state_tax, local_tax, fica)

    if "-p" in sys.argv:
        plot_bonus(bonus, federal_tax, state_tax, local_tax, fica)

    if "-o" in sys.argv:
        print(info["Net Bonus"])
        sys.exit(0)

    print()
    for key, value in info.items():
        print(f"{key}: ${value:,.2f}")
    print()


if __name__ == "__main__":
    run()
