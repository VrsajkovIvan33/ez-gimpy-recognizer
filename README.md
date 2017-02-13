# ez-gimpy-recognizer

Recognizing the word contained in a EZ-Gimpy captcha image.

The images and the files with words can be downloaded from [here](https://drive.google.com/file/d/0BwNBoW5RIOOZa29McEVCeTZaVUk/view?usp=sharing).

## Usage ##
**Note:** The python-levenshtein package must be installed in order to run the recognizer or the tests. This can be done with the `pip install` command.

`pip install python-levenshtein`

If you are having trouble installing the package, you can download the binaries from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein). Make sure to download the correct version, specific to the platform you are using. The installation is done in the same way, just specify the route to the binaries in the argument

To run the recognizer on a single image, specify the relative route to the image in the argument. For an example:

`python Recognizer.py Dataset/001.jpg`

The calculated words will appear on the terminal display.

Running without any specified arguments means that all images from the *Dataset* folder will be processed and the results will be placed in the *out.txt* file (make sure to download the *Dataset* folder first, using the link mentioned in the beginning).

## About ##

The process of calculating the most probable words is divided in three steps:

1. **Image processing** - remove the noise and extract the estimated regions that contain letters
2. **Prediction** - predict a letter for every region using the [K-nearest neighbour algorithm](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
3. **Find probable words** - using the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance), find the most probable words that can be found in the *word_collection.txt* file using the calculated letters and their order  

## Testing ##
All of the testing is done referencing the *correct_words.txt* file that contains the correct words for every image in the *Dataset* folder. The data that is being tested should be in the *out.txt* file.

There are three results of the test:

1. The number of correctly predicted words - checks whether the correct word is contained in the set of most probable words
2. The average ratio using the Levenshtein distance between the correct words and a word with the highest success ratio from the respectful set of most probable words
3. The average ratio using the Levenshtein distance between the correct words and all words from the respectful set of most probable words


