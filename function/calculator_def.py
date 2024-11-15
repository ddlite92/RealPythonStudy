import math

def main():
    print("This script is to calculate the result of square, square root, modulus, exponent and floor division.")
    x = int(input("Please input the first number: "))
    y = int(input("Please input the second number: "))
    # print = "What arimethic calculation you want to do with the number: \n square, square root, modulus, exponent or floor division: "
    square_x, 
    

def calculate(x, y):
    square_x = x * y
    square_root = x / y
    modulus = x % y
    exponent = x**y
    floor_division = x // 2
    return square_x, square_root, modulus, exponent, floor_division


main()

"""
corrected

import math

def main():
    print("This script is to calculate the result of square, square root, modulus, exponent, and floor division.")
    x = int(input("Please input the number you're interested in: "))

    square, square_root, modulus, exponent, floor_division = calculate(x)

    print("The square of that number is:", square)
    print("The square root of that number is:", square_root)
    print("The modulus of that number is:", modulus)
    print("The exponent of that number is:", exponent)
    print("The floor division of that number is:", floor_division)

def calculate(x):
    square = x * x
    square_root = math.sqrt(x)
    modulus = x % 10  # Assuming you want modulus with base 10
    exponent = x ** x
    floor_division = x // 2  # Assuming you want floor division with divisor 2

    return square, square_root, modulus, exponent, floor_division

if __name__ == "__main__":
    main()
"""

