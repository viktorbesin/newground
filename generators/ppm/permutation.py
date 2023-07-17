import random


def generate_permutation(t_len, frac, seed):

    random.seed(seed)

    t_permutation = [x for x in range(1, 1 + t_len)]
    p_permutation = [x for x in range(1, 1 + int(t_len/frac))]
    #p_permutation = [x for x in range(1, 10)]

    t_indices = t_permutation.copy()
    random.shuffle(t_permutation)

    p_indices = p_permutation.copy()
    random.shuffle(p_permutation)

    output_prg = ""

    for t_index in t_indices:
        output_prg = output_prg + f"t({t_index},{t_permutation[t_index - 1]}).\n"

    for p_index in p_indices:
        output_prg = output_prg + f"p({p_index},{p_permutation[p_index - 1]}).\n"

    output_prg = output_prg + f"patternlength({len(p_indices)}).\n"

    for index in range(1, len(p_indices) + 1):
        output_prg = output_prg + f"kval({index}).\n"


    output_prg = output_prg + """
% ENCODING ADDITIONAL PART
1 <= { subt(K,I,E) : t(I,E) } <= 1 :- kval(K), patternlength(L).
:- subt(K1,I1,_), subt(K2,I2,_), K1<K2, I1 >= I2.

solution(K,E) :- subt(K,_,E).
"""

    return output_prg


if __name__ == '__main__':

    frac = 5
    seed = 11904657

    for length in range(75,300, 3):
        output_prg = generate_permutation(length, frac,  seed)

        if length < 100:
            f = open(f"instance_0{length}.lp", "w")
        else:
            f = open(f"instance_{length}.lp", "w")

        f.write(output_prg)






