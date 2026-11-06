
def calculate_total(price, quantity):
    total = price * quantity
    return total


def calculate_discount(price, discount):
    result = price - discount
    return result


def process_user_input(user_input):
    result = eval(user_input)
    return result


def main():
    password = "admin123"

    unused_variable = 100

    print("Welcome to SonarQube Demo")

    print(calculate_total(100, 5))

    print(calculate_discount(500, 50))


if __name__ == "__main__":
    main()
