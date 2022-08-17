# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_pascalsTri(num):
    num = num + 1
    num_of_spaces = num - 1
    num_of_characters = 0
    for i in range(num):
        print(' ' * (num_of_spaces),end='')
    #    num_of_characters += num_of_spaces
        for a in range(i + 1):
            factorialI = factorial(i)
            factorialA = factorial(a)
            factorialIA = factorial(i - a)
            printNum = int(factorialI/(factorialA*factorialIA))
            num_of_characters += len(str(printNum))
            print(printNum,end=' '*1,sep='')
        print()
        num_of_spaces -= 1

def factorial(num):
    if(num == 0):
        return 1
    if(num == 1):
        return 1
    else:
        factorialReturn = num*factorial(num-1)
        return factorialReturn


if __name__ == '__main__':
    print_pascalsTri(5)

