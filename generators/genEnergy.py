
import sys
import random


def generate_power_plants(number, lower_energy, higher_energy, lower_position, higher_position):

    power_plants = []
    locations = []

    for i in range(number):

        e = random.randint(lower_energy, higher_energy)
        l = random.randint(lower_position, higher_position)

        
        power_plants.append(f"p({i},{e}).")
        locations.append(f"loc({i},{l}).")

    return (power_plants, locations)


if __name__ == '__main__':

    number = int(sys.argv[1])
    le = int(sys.argv[2])
    he = int(sys.argv[3])
    lp = int(sys.argv[4])
    hp = int(sys.argv[5])
        

    power_plants, locations = generate_power_plants(number, le, he, lp, hp)

    for power_plant in power_plants:
        print(power_plant)

    for location in locations:
        print(location)
    





