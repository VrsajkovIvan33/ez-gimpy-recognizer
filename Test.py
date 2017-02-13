import Levenshtein

with open("out.txt") as out_file:
    read_data = out_file.read()
    results = read_data.split('\n')

with open("correct_words.txt") as correct_words_file:
    read_data = correct_words_file.read()
    correct_words = read_data.split('\n')

# the total number of captcha images
total_counter = 0
# the number of correctly identified words
correct_counter = 0

# the sum of Levenshtein ratios between all probable words and the correct words, respectfully
soft_ratio_all_words = 0
# the sum of Levenshtein ratios between the best matching probable words and the correct words, respectfully
soft_ratio_only_best = 0
# the number of all probable words
soft_total_all_words_counter = 0
# the number of the best matching words (same as the total counter)
soft_total_only_best_counter = 0

for index, line in enumerate(results):
    total_counter += 1
    result = line.split(' ')
    # hard test
    for single_result in result:
        # skip the file name
        if single_result != result[0] and single_result.lower() == correct_words[index]:
            correct_counter += 1
            break
    # soft test
    max_ratio = 0
    for single_result in result:
        if single_result != result[0]:
            ratio = Levenshtein.ratio(single_result.lower(), correct_words[index])
            soft_ratio_all_words += ratio
            soft_total_all_words_counter += 1
            if ratio > max_ratio:
                max_ratio = ratio
    soft_ratio_only_best += max_ratio
    soft_total_only_best_counter += 1

print "Hard test"
print "Total: " + str(total_counter)
print "Correct: " + str(correct_counter)

print "Soft test - use only the best matching words"
print "Success: " + str(soft_ratio_only_best/soft_total_only_best_counter)

print "Soft test - use all returned words"
print "Success: " + str(soft_ratio_all_words/soft_total_all_words_counter)
