from formatted_weights import get_formatted

num_gens = 50
num_individuals = 30

def print_consistent_top_id(start, end, top):
    id_dict = {}
    for i in range(start, end+1):
        with open(f"generation_{i}.txt","r") as f:
            for _ in range(top):
                individual = eval(f.readline())
                id = individual['id']

                if id not in id_dict:
                    id_dict[id] = 1
                else:
                    id_dict[id] += 1

    id_sorted = sorted(id_dict.items(), key=lambda a: a[1], reverse=True)
    for element in id_sorted:
        print(element)

def print_best_median(start, end, min):
    individual_lst = []
    for i in range(start, end+1):
        with open(f"generation_{i}.txt","r") as f:
            for _ in range(num_individuals):
                individual = eval(f.readline())
                median = individual['median_score']

                if median > min:
                    individual_lst.append(individual)

    individual_sorted = sorted(individual_lst, key=lambda a: a['median_score'], reverse=True)
    for individual in individual_sorted:
        print(f"{get_formatted(individual)} (median {individual['median_score']})")

    return individual_sorted

def print_highest_score(start, end, min):
    individual_lst = []
    for i in range(start, end+1):
        with open(f"generation_{i}.txt","r") as f:
            for _ in range(num_individuals):
                individual = eval(f.readline())
                max_score = individual['scores'][4]

                if max_score > min:
                    individual_lst.append(individual)
    
    individual_sorted = sorted(individual_lst, key=lambda a: a['id'], reverse=True)
    for individual in individual_sorted:
        print(f"{get_formatted(individual)} (max score {individual['scores'][4]})")

    return individual_sorted
        
if __name__ == '__main__':
    start_gen = int(input("Enter start gen: "))
    end_gen = int(input("Enter end gen: "))
    
    top_amt = int(input("Enter top amt: "))
    print_consistent_top_id(start_gen, end_gen, top_amt)

    print("\n\n\n")

    min_median = int(input("Enter minimum median: "))
    lst_1 = print_best_median(start_gen, end_gen, min_median)
    
    min_max_score = int(input("Enter minimum max score: "))
    lst_2 = print_highest_score(start_gen, end_gen, min_max_score)

    print("\n\n\n")

    for individual in lst_2:
        if individual not in lst_1 and (individual['scores'][2] > 47000 or individual['scores'][4] > 54000):
            print(f"{get_formatted(individual)} (max score {individual['scores'][4]})")