# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize, sent_tokenize
# from nltk import pos_tag

# # Download necessary NLTK data
# nltk.download("punkt")
# nltk.download("averaged_perceptron_tagger")
# nltk.download("stopwords")


# def extract_keywords(text):
#     # Convert text to lowercase
#     text = text.lower()

#     # Prepare the list of stopwords
#     stop_words = set(stopwords.words("english"))

#     # Tokenize the text
#     words = word_tokenize(text)

#     # Filter out stopwords and non-alpha words
#     words = [word for word in words if word.isalpha() and word not in stop_words]

#     # Perform POS tagging
#     tagged = pos_tag(words)

#     # Extract nouns and adjectives as keywords
#     keywords = [
#         word for word, tag in tagged if tag in ("NN", "NNS", "NNP", "NNPS", "JJ")
#     ]

#     return keywords


# # text = "Your input string with potential Keywords."
# # keywords = extract_keywords(text)


# def make_score_list(search_string: str, strings_to_search: list) -> list:
#     # print(search_string)
#     lower_case_keywords = extract_keywords(search_string)
#     # print(keywords)
#     scores = []
#     # print(strings_to_search)
#     for this_string in strings_to_search:
#         this_string = this_string.lower()
#         this_score = 0
#         for keyword in lower_case_keywords:
#             # this_score += this_string.count(keyword)
#             if this_string.find(keyword) > -1:
#                 this_score += 1
#         scores.append(this_score)
#     return scores


# def sort_string_list(search_string: str, strings_to_search: list):
#     # print(search_string)
#     # print(strings_to_search)
#     scores = make_score_list(search_string, strings_to_search)
#     # print(scores)
#     # Your lists
#     # strings = ['james', 'bob', 'the zohar is crazy', 'i am jewish']
#     # ranks = [0, 2, 4, 6]

#     # Zip the ranks and strings together
#     zipped = zip(scores, strings_to_search)

#     # Sort the zipped list based on ranks
#     sorted_zipped = sorted(zipped, reverse=True)

#     # Extract the strings from the sorted zipped list
#     sorted_strings = [string for score, string in sorted_zipped if score != 0]

#     # print(sorted_strings)
#     return sorted_strings
