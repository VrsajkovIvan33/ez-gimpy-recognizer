import os
import sys
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.measure import label, regionprops
from skimage.transform import resize
from skimage.morphology import dilation, erosion, square, closing
from sklearn.neighbors import KNeighborsClassifier
import Levenshtein


def create_classifier():
    data = []
    targets = []
    for letter_folder in os.listdir('Training set'):
        directory_path = os.path.join('Training set', letter_folder)
        # for each letter image, first create a binerized image, then process it to join the regions that are close one
        # to another, then use the image of the largest region and modify its size - use the processed image as data
        for letter_file in os.listdir(directory_path):
            train_img = imread(os.path.join(directory_path, letter_file))/255.0
            train_img_bin = 1 - (train_img > 0.5)
            train_bin_closing = closing(train_img_bin, selem=square(3))
            train_labeled = label(train_bin_closing)
            train_regions = regionprops(train_labeled)
            largest_region = None
            largest_area = 0
            for single_train_region in train_regions:
                if single_train_region.area > largest_area:
                    largest_area = single_train_region.area
                    largest_region = single_train_region
            train_image = resize(largest_region.image, (25, 25)) > 0.5
            data.append(train_image.flatten())
            targets.append(letter_folder)
    # use only 1 neighbour because some letters have only one image representing them
    return KNeighborsClassifier(n_neighbors=1).fit(data, targets)


def test_classifier(knn):
    test_img = imread('Training Set/I/UGCCGGUGGGCGGGCAGAAU.jpg')
    # test_img = imread('Training Set/A/a2.png')
    # test_img = imread('Training Set/I/GCGAGCCGCGGGGAACAGGU.jpg')
    test_image_too = test_img/255.0
    test_bin = 1 - (test_image_too > 0.5)
    test_bin_closing = closing(test_bin, selem=square(3))
    train_labeled = label(test_bin_closing)
    train_regions = regionprops(train_labeled)
    largest_region = None
    largest_area = 0
    for single_train_region in train_regions:
        if single_train_region.area > largest_area:
            largest_area = single_train_region.area
            largest_region = single_train_region
    train_image = resize(largest_region.image, (25, 25)) > 0.5
    print 'Rezultat: ' + str(knn.predict(train_image.flatten().reshape(1, -1)))


# sort the regions from left to right in order to get the order of the letters later
def sort_by_centroid(regions_array):
    sorted_regions = []
    while len(regions_array) > 0:
        min_index = -1
        min_element = 1000000
        for index, reg_from_array in enumerate(regions_array):
            if reg_from_array.centroid[1] < min_element:
                min_element = reg_from_array.centroid[1]
                min_index = index
        sorted_regions.append(regions_array.pop(min_index))
    return sorted_regions


# distance between the estimated letters form the classifier and a word
def calculate_distance(given_word, target_word):
    # distance = 0
    # for index, letter in enumerate(given_word):
    #     if letter != target_word[index]:
    #         # Manja je greska ako se pomesaju I i L
    #         if letter == 'I' and target_word[index] == 'L':
    #             distance += 0.5
    #         elif letter == 'L' and target_word[index] == 'I':
    #             distance += 0.5
    #         else:
    #             distance += 1
    # return distance
    given_word_to_string = ''
    for array in given_word:
        given_word_to_string += array[0]
    return Levenshtein.ratio(given_word_to_string, target_word)


# processing of the image in order to find the suitable regions (depending on the type of image)
def find_regions(image_name):
    img = imread(image_name)
    img_gray = rgb2gray(img)
    img_bin = 1 - (img_gray > 0.3)
    labeled_img = label(img_bin)
    regions = regionprops(labeled_img)
    estimated_regions = []

    if len(regions) < 2:
        # this means that there is a black grid on the image and it needs to be removed by using erosion; the letters
        # are reformed later with dilation
        print 'black grid'

        # because this image doesn't have noise, the threshold can be higher in order to get as much of a letter as
        # possible
        img_bin_black_grid = 1 - (img_gray > 0.5)

        img_bin_erosion_black_grid = erosion(img_bin_black_grid, selem=square(2))
        img_bin_fixed_black_grid = dilation(img_bin_erosion_black_grid, selem=square(2))
        labeled_img_black_grid = label(img_bin_fixed_black_grid)
        estimated_regions = regionprops(labeled_img_black_grid)

    elif len(regions) < 8:
        # there is no need for processing
        print 'regular'
        estimated_regions = regions

    else:
        # check whether the letters are whole or not
        possible_regions = []
        for region in regions:
            if region.area > 100:
                possible_regions.append(region)

        if len(possible_regions) > 3:
            # this means that all letters are whole and that there is no need for further processing to reform them,
            # just take the large enough regions
            print 'noise, whole letters'
            estimated_regions = possible_regions

        elif len(regions) > 100:
            # this means that there is noise, but the letters are not whole - try to connect the parts of letters and
            # then take the large enough regions
            print 'noise, partial letters'
            img_bin_noise = 1 - (img_gray > 0.3)
            img_bin_noise_dilation = closing(img_bin_noise, selem=square(2))
            labeled_img_noise = label(img_bin_noise_dilation)
            noise_regions = regionprops(labeled_img_noise)
            for region in noise_regions:
                if region.area > 25:
                    estimated_regions.append(region)

        else:
            # this means that either there is noise in the letters or there isa a white grid - the parts of the letters
            # need to be connected together
            print 'noise or white grid'
            # create a new binarized image with a bigger threshold in order to get as much of the letters as possible
            # without catching some of the background (it won't always be white)
            img_bin_separated = 1 - (img_gray > 0.45)
            img_bin_separated_closing = closing(img_bin_separated, selem=square(3))
            labeled_img_separated = label(img_bin_separated_closing)
            estimated_regions = regionprops(labeled_img_separated)

    return estimated_regions


# use the classifier to predict the letters from the given regions
def find_letters(knn, estimated_regions):
    found_regions = []
    estimated_letters = []
    for found_region in estimated_regions:
        bbox = found_region.bbox
        width = bbox[3] - bbox[1]
        # use only the regions that are the appropriate size and shape
        if found_region.area >= 40 and width < 50:
            found_regions.append(found_region)

    letter_regions = sort_by_centroid(found_regions)
    for letter_region in letter_regions:
        letter_image = resize(letter_region.image, (25, 25)) > 0.5
        estimated_letters.append(knn.predict(letter_image.flatten().reshape(1, -1)))

    return estimated_letters


# get the most likely words from the order of the letters - return all words with the biggest ratio
def find_probable_words(estimated_letters, words):
    max_ratio = 0
    best_matching_words = []
    for word in words:
        if len(word) == len(estimated_letters) and '-' not in word and '\'' not in word:
            distance = calculate_distance(estimated_letters, word.upper())
            if distance > max_ratio:
                max_ratio = distance
                best_matching_words = []
                best_matching_words.append(word)
            elif distance == max_ratio:
                best_matching_words.append(word)
    return best_matching_words


with open("word_collection.txt") as word_collection:
    read_data = word_collection.read()
    words = read_data.split('\n')
knn = create_classifier()

# if a path to an image is specified, process only the specified image
if len(sys.argv) == 2:
    regions_after_processing = find_regions(sys.argv[1])
    letters = find_letters(knn, regions_after_processing)
    probable_words = find_probable_words(letters, words)
    print 'Most probable words:'
    for word in probable_words:
        print word
# run through all images in the 'Dataset' folder
else:
    results = []
    for captcha_image in os.listdir('Dataset'):
        print os.path.join('Dataset', captcha_image)
        regions_after_processing = find_regions(os.path.join('Dataset', captcha_image))
        letters = find_letters(knn, regions_after_processing)
        results.append([captcha_image] + find_probable_words(letters, words))

    with open("out.txt", 'w') as out_file:
        for result in results:
            for single_word in result:
                out_file.write(str(single_word) + ' ')
            out_file.write('\n')
