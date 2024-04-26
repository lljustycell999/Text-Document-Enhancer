import numpy as np


def calculate_accuracy(text, clean_text):
    """
    Calculates the accuracy of how well Tesseract OCR was able to read the preprocessed image in contrast to its
    clean image counterpart.

    :param text: The text extracted by Tesseract OCR from the preprocessed image.
    :type text: str
    :param clean_text: The text extracted by Tesseract OCR from the clean image counterpart.
    :type clean_text: str

    :return: The percentage of words between text and clean_text that match and are in the correct order.
    :rtype: float
    """

    text_words = text.split()
    clean_text_words = clean_text.split()

    # Implement the Levenshtein distance algorithm between the two texts

    # Create a distance_matrix to keep track of the total cost distance between the two texts
    # (add 1 extra row and column for padding)
    distance_matrix = np.zeros((len(text_words) + 1, len(clean_text_words) + 1))
    for i in range(len(text_words) + 1):
        for j in range(len(clean_text_words) + 1):

            # Add padding for the first row and column of the distance_matrix. These are the base costs/distances
            # for comparing an empty string to a non-empty string.
            if i == 0:
                distance_matrix[i][j] = j
            elif j == 0:
                distance_matrix[i][j] = i

            # Check if the current text_word matches the current clean_text_word. If so, no changes need to be made,
            # and we keep the cost the same.
            elif text_words[i - 1] == clean_text_words[j - 1]:
                distance_matrix[i][j] = distance_matrix[i - 1][j - 1]

            # If it isn't, check neighbors that have already been calculated, find the minimum distance, and add 1
            # (1 is added because there has to be a cost when the words don't match)
            else:
                distance_matrix[i][j] = 1 + min(distance_matrix[i - 1][j],
                                                distance_matrix[i][j - 1],
                                                distance_matrix[i - 1][j - 1])

    # Get the maximum possible distance between the two texts
    max_distance = max(len(text_words), len(clean_text_words))

    # Calculate the accuracy using max_distance and the final calculated distance
    accuracy = ((max_distance - distance_matrix[-1][-1]) / max_distance) * 100

    return accuracy
