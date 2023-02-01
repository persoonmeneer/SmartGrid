import smartgrid
import smartgrid2
import baseline
import baseline2
import smartgrid_random_annealing
import sys
import os

if __name__ == "__main__":
   
    argument = sys.argv[1]

    while argument not in ["smartgrid", "smartgrid2", "baseline", "baseline2", "smartgrid_random_annealing"]:
        argument = input("Enter a valid option: ")

    if argument == 'baseline':
        os.system('python3 baseline.py')
    elif argument =='smartgrid':
        os.system('python3 smartgrid.py')
    elif argument =='smartgrid2':
        os.system('python3 smartgrid2.py')
    elif argument =='smartgrid_random_annealing':
        os.system('python3 smartgrid_random_annealing.py')

