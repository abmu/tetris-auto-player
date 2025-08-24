def get_formatted(individual):
    return_str = ''
    curr_letter = 'a'
    for key in individual:
        if key in ['id', 'scores', 'median_score', 'mean_score']:
            continue
        return_str += f'{curr_letter}='
        if individual[key] >= 0:
            return_str += ' '
        return_str += f'{individual[key]:.4f}, '
        curr_letter = chr(ord(curr_letter) + 1)
    return_str = return_str[:-2] + f' (id {individual["id"]})' # remove extra comma and space at the end
    return return_str

if __name__ == '__main__':
    individual_dict = eval(input('Copy and paste individual dict: '))
    print(get_formatted(individual_dict))