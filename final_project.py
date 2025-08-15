# final_python.py

"""
Personal Budget Tracker (CLI)

What it does:
- Prompts for monthly income
- Lets the user add multiple expense categories and amounts
- Prevents allocating more than the available income
- Shows total budgeted, remaining (saved) amount, and per-category % of income
- Asks for a monthly saving goal and reports whether it's met
- Handles bad input gracefully and exits cleanly on Ctrl+C / EOF

Error handling approach:
- Input helpers loop until valid input is provided (no traceback shown to the user)
- Ctrl+C / EOF exits the program with a friendly message and a conventional exit code (130)
- A last-resort exception handler prevents unhandled crashes from showing a traceback
"""

import sys  # used for clean exits via sys.exit()


def get_positive_float(prompt: str) -> float:
    """
    Prompt until a valid non-negative number is entered.

    Returns:
        float: The parsed value (>= 0).

    Error handling:
    - Re-prompts on non-numeric input or negative values.
    - Cleanly exits on EOFError/KeyboardInterrupt (Ctrl+D/Ctrl+C).
    """
    while True:
        try:
            s = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            # User aborted input: exit gracefully with conventional code for SIGINT
            print("\nInput cancelled. Exiting.")
            sys.exit(130)

        try:
            value = float(s)
        except ValueError:
            # Non-numeric input (e.g., empty string, letters, etc.)
            print("Please enter a valid number (e.g., 1234.56).")
            continue

        if value < 0:
            # Guard against negative amounts
            print("Value cannot be negative. Try again.")
            continue

        return value


def get_yes_no(prompt: str) -> bool:
    """
    Prompt for a yes/no answer.

    Returns:
        True for yes (y/yes), False for no (n/no).

    Error handling:
    - Re-prompts until a valid choice is entered.
    - Cleanly exits on EOFError/KeyboardInterrupt.
    """
    while True:
        try:
            s = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            sys.exit(130)

        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False

        print("Please enter 'y' or 'n'.")


def get_non_empty_text(prompt: str, *, max_len: int = 50) -> str:
    """
    Prompt for a non-empty text value (used for category names).

    Args:
        max_len: Maximum allowed length to avoid overly long labels.

    Error handling:
    - Re-prompts if empty or too long.
    - Cleanly exits on EOFError/KeyboardInterrupt.
    """
    while True:
        try:
            s = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            sys.exit(130)

        if not s:
            print("Category cannot be empty. Try again.")
            continue

        if len(s) > max_len:
            print(f"Category too long (max {max_len} characters). Try again.")
            continue

        return s


def create_budget(income: float):
    """
    Interactively build a budget without exceeding the provided income.

    Returns:
        tuple: (budget_list, total_budget, amount_saved)
            - budget_list: list of dicts like {"category": str, "amount": float}
            - total_budget: sum of all amounts
            - amount_saved: income - total_budget (remaining)

    Notes on constraints:
    - Never allows the running total to exceed income.
    - Stops when the user chooses to stop or when income is fully allocated.
    """
    active = True  # loop control flag (user can stop adding categories)
    budget = []    # accumulates {"category": name, "amount": value}
    total_budget = 0.0  # running sum of all category amounts

    # Continue while we still have income to allocate and the user wants to continue
    while total_budget < income and active:
        # Ask for a category name (validated to be non-empty)
        category = get_non_empty_text("What category of spending? ")

        # How much money is left to allocate
        available = income - total_budget

        # Inner loop: get a valid amount that does not exceed the remaining available income
        while True:
            amount = get_positive_float(
                f"How much will you spend in this category? (available {available:.2f}) "
            )
            if amount > available:
                # Prevent over-allocation and explain why
                print("Total budget would exceed income. Please enter a smaller amount.")
                continue
            break  # amount is valid for this category

        # Update totals and record this expense
        total_budget += amount
        print(f"Total budget so far: {total_budget:.2f}")
        budget.append({"category": category, "amount": amount})

        # If we've exactly allocated the full income, we're done
        if total_budget >= income:
            print("You've allocated all of your income ✅")
            break

        # Ask the user if they want to add another category
        active = get_yes_no("Do you want to add another category to your budget? (y/n) ")

    # Remaining (saved) money after all allocations
    amount_saved = income - total_budget
    return budget, total_budget, amount_saved


def main():
    """
    Program entry point:
    - Collect income
    - Build budget interactively
    - Display summary and percentages
    - Ask for a saving goal and report whether it's met

    Error handling:
    - SystemExit is re-raised to preserve clean exits from helper functions.
    - A broad Exception handler avoids ugly tracebacks for unexpected issues.
    """
    try:
        # 1) Ask for gross monthly income
        gross = get_positive_float("Enter your income: ")

        # 2) Build the budget with validated inputs
        budget, total_budget, amount_saved = create_budget(gross)

        # 3) Summary of allocations
        print("\nYour budget has been created")
        for item in budget:
            # Format amounts to 2 decimal places for currency-like display
            print(f"Category: {item['category']}, Amount: {item['amount']:.2f}")

        print(f"\nYour total income is {gross:.2f}")
        print(f"Total budgeted: {total_budget:.2f}")
        print(f"You saved {amount_saved:.2f}")

        # 4) Optional: per-category percentage of income
        #    Guard against division by zero by checking gross > 0
        if gross > 0 and budget:
            print("\nExpense breakdown (% of income):")
            for item in budget:
                pct = (item["amount"] / gross) * 100  # percentage of income
                print(f"  {item['category']}: {pct:.2f}%")

        # 5) Saving goal: prompt and check against the remaining (saved) amount
        goal = get_positive_float("\nEnter your monthly saving goal (0 for none): ")

        if amount_saved >= goal:
            # Goal is achievable (or already achieved) with current budget
            print("Saving goal met ✅")
        else:
            # Provide the shortfall and a helpful hint on what to change
            shortfall = goal - amount_saved
            print(f"Saving goal NOT met ❌ (shortfall {shortfall:.2f})")

            # For context: how much total spending would need to be reduced (or income increased)
            # to meet the goal, i.e., compare current total budget to (income - goal).
            available_to_spend_for_goal = gross - goal
            overspend_vs_goal = total_budget - available_to_spend_for_goal
            if overspend_vs_goal > 0:
                print(
                    f"To meet your goal, reduce expenses by at least {overspend_vs_goal:.2f} "
                    "or increase income."
                )

    except SystemExit:
        # Allow clean exits from get_* helpers (we intentionally called sys.exit)
        raise
    except Exception:
        # Last-resort safety net to avoid raw tracebacks in the user interface.
        # During development, uncomment the traceback lines to debug:
        # import traceback
        # traceback.print_exc()
        print("Unexpected error occurred. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    # Standard Python entry-point guard
    main()