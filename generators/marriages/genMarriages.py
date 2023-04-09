import sys

from genMarriage import gen_marriage

if __name__ == '__main__':

    prob = int(sys.argv[1])

    assert(prob >= 0)
    assert(prob <= 100)

    for i in range(382, 401, 3):
        output = gen_marriage(i, prob)

        write_string = ""
        for string in output:
            write_string += f"{string}\n"

        if i < 10:
            file_name =f"instance_00{i}.lp"
        elif i < 100:
            file_name =f"instance_0{i}.lp"
        else:
            file_name =f"instance_{i}.lp"

        f = open(file_name, "w")

        f.write(write_string)

        f.close()




