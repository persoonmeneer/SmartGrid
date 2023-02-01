"""
This program will launch smartgrid simulations or the baseline
"""

import os
from typing import Final

# options which kind of programs can be runned
OPTIONS: Final = ["smartgrid", "baseline"]

if __name__ == "__main__":
    # give user the choices of programs
    print("What would you like to run? The options are:")
    for program in OPTIONS:
        if program == OPTIONS[-1]:
            print(program)
        else:
            print(f"{program}, ", end=" ")

    # ask user for which program to run
    run = input()

    # keep asking until valid input
    while run not in OPTIONS:
        print("Enter a valid option. The options are:")
        for program in OPTIONS:
            if program == OPTIONS[-1]:
                print(program)
            else:
                print(f"{program}, ", end=" ")

        run = input()

    # clear terminal
    os.system('clear')

    # clear terminal and run the given program
    if run == 'baseline':
        os.system('clear')
        os.system('python3 Code/baseline.py')
    else:
        os.system('clear')
        os.system('python3 Code/smartgrid.py')
