import sys

from genEnergy import generate_power_plants

if __name__ == '__main__':

    start_number = int(sys.argv[1])
    step = int(sys.argv[2])
    end_number = int(sys.argv[3])
    le = int(sys.argv[4])
    he = int(sys.argv[5])
    lp = int(sys.argv[6])
    hp = int(sys.argv[7])

    assert(start_number <= end_number)
    assert(step > 0)

    for i in range(start_number,end_number,step):
        power_plants, locations = generate_power_plants(i, le, he, lp, hp)

        write_string = ""
        for power_plant in power_plants:
            write_string += power_plant + "\n"

        for location in locations:
            write_string += location + "\n"

        file_name = ""

        if i < 10:
            file_name =f"instance_00{i}.lp"
        elif i < 100:
            file_name =f"instance_0{i}.lp"
        else:
            file_name =f"instance_{i}.lp"

        f = open(file_name, "w")

        f.write(write_string)

        f.close()


