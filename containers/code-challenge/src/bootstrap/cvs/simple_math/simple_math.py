import argparse

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Can't divide by zero!")
    return x / y

parser = argparse.ArgumentParser()
parser.add_argument("--x", type=float, default=1.0,
                    help="First number")
parser.add_argument("--y", type=float, default=1.0,
                    help="Second number")
parser.add_argument("--operation", type=str, default="add",
                    help="Operation to perform - add, subtract, multiply, divide")

args = parser.parse_args()

if args.operation == "add":
    result = add(args.x, args.y)
elif args.operation == "subtract":
    result = subtract(args.x, args.y)
elif args.operation == "multiply":
    result = multiply(args.x, args.y)
elif args.operation == "divide":
    result = divide(args.x, args.y)
else:
    raise Exception("Invalid operation!")

print("Result:", result)
