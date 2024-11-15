
def user_input():
    x = int(input("Please input number your interesed in: "))
    arimethic = input("What arimethic calculation you want to do with the number: \n square, square root, modulus, exponent or floor division: ")
    return x, arimethic
    
def calculate(x, arimethic):
    if arimethic == "square":
        return x * x
    elif arimethic == "square root": 
        return x / x
    elif arimethic == "modulus":
        return x % x
    elif arimethic == "exponent":
        return x**x
    elif arimethic == "floor_division":
        return x // x

def main():
    print("This script is to calculate the result of square, square root, modulus, exponent and floor division.")
    x, arimethic = user_input()
    result = calculate(x, arimethic)
    print("The answer is: ", result)

main()


