import pandas as pd
import pronouncing
import speech_recognition as sr
import streamlit as st
import Levenshtein
import difflib
from annotated_text import annotated_text

# Import functions from the utility module
from extra.utility import text_preprocessing, create_unique_word_dict, find_sentence_with_word

# Reading the text from the input folder
texts = pd.read_csv('data/sentences_test.csv')
texts = [x for x in texts['text']]

# Creating a placeholder for the scanning of the word list
all_text = []

for text in texts:
    # Cleaning the text
    text = text_preprocessing(text)
    # Appending to the all text list
    all_text += text 

unique_word_dict = create_unique_word_dict(all_text)

# Initialize the Streamlit app
st.title("Speech Recognition App")
st.write("Speak the phrase: "  + texts[0])

# The phrase that the user should speak
# correct_phrase = sentences

# Initialize recognized_phrase variable
recognized_phrase = None

# Function to check the phrase and return the recognized text
def check_phrase():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        # Recognize the speech using the Google Web Speech API
        text = recognizer.recognize_google(audio)
        st.write("You said: " + text.capitalize())

        # Check if the spoken phrase matches the correct phrase
        if texts[0].lower() == text.lower():
            st.success("You spoke the correct phrase!")
        else:
            st.error("You didn't speak the correct phrase.")

        # Capitalize the first letter of the recognized text
        capitalized_text = text.capitalize()

        return capitalized_text  # Return the recognized text with the first letter capitalized
    
    except sr.UnknownValueError:
        st.warning("Could not understand the speech.")
        return None  # Return None if speech couldn't be recognized
    except sr.RequestError as e:
        st.error("Request error: {0}".format(e))
        return None  # Return None in case of a request error

# Function to find rhymes in the word list
def find_rhymes_in_list(word, unique_word_dict):
    # Get a list of words that rhyme with the given word
    rhymes = pronouncing.rhymes(word)
    
    # Filter rhymes to include only those in the word list
    rhymes_in_list = [rhyme for rhyme in rhymes if rhyme in unique_word_dict]
    
    return rhymes_in_list

# Create a button in Streamlit to trigger speech recognition
if st.button("Start Speech Recognition"):
    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Execute the function to check the phrase and store the recognized phrase
    recognized_phrase = check_phrase()

# Now you can use the recognized_phrase variable as needed
if recognized_phrase is not None:
    # Compute the Levenshtein distance between the two phrases
    distance = Levenshtein.distance(texts[0], recognized_phrase)

    # Calculate the similarity ratio
    max_length = max(len(texts[0]), len(recognized_phrase))
    similarity_ratio = 1 - (distance / max_length)

    similarity_threshold = 0.9  # Adjust the threshold as needed

    st.write("Similarity Ratio:", similarity_ratio)

    if similarity_ratio >= similarity_threshold:
        st.success("The recognized phrase is similar enough to the correct phrase.")
    else:
        st.error("The recognized phrase is not similar to the correct phrase.")

        st.write("Differences:")
        html = ""
        correct_words = texts[0].split()
        recognized_words = recognized_phrase.split()

        for word in correct_words:
            if word in recognized_words:
                html += f'<span style="color:white;">{word}</span> '
            else:
                html += f'<span style="color:red;">{word}</span> '

        st.markdown(html, unsafe_allow_html=True)

    differences = [word[2:] for word in difflib.ndiff(texts[0].split(), recognized_phrase.split()) if word[0] == '-']

    st.write("\nIncorrect words:", differences)

    # Find rhymes for the first incorrect word
    if differences:
        input_word = differences[0]
        rhymes = find_rhymes_in_list(input_word, unique_word_dict)

        if rhymes:
            st.write(f"Rhymes for '{input_word}' in the word list: {', '.join(rhymes)}")
        else:
            st.write(f"No rhymes found for '{input_word}' in the word list.")

        # Find the first sentence containing the first word from the word list
        target_word = rhymes[0] if rhymes else ""
        result_sentence = find_sentence_with_word(target_word, texts)

        if result_sentence:
            st.write(f"The first sentence containing '{target_word}': {result_sentence}")
        else:
            st.write(f"No sentence found containing '{target_word}'.")
