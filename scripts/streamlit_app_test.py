import pandas as pd
import pronouncing
import speech_recognition as sr
import streamlit as st
import Levenshtein
import difflib

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

# Initialize recognized_phrase variable and result_sentence
recognized_phrase = None
result_sentence = []

# Initialize the list to store result sentences
result_sentences_list = ["She had to abandon her old car and buy a new one"]
prev_result_sentence = ""


# Function to check the phrase and return the recognized text
def check_phrase(result_sentence):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        # Recognize the speech using the Google Web Speech API
        text = recognizer.recognize_google(audio)
        st.write("You said: " + text.capitalize())

        # Check if the spoken phrase matches the correct phrase
        if result_sentence.lower() == text.lower():
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

# Create a button in Streamlit to trigger the start of the speech recognition loop
if st.button("Start Speech Recognition"):
    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Execute the loop until a certain condition is met (you need to define the condition)
    while True:
        # Determine the instruction for the user
        instruction_text = "Speak the phrase: " + result_sentences_list[-1]
        st.write(instruction_text)

        # Execute the function to check the phrase and store the recognized phrase
        recognized_phrase = check_phrase(result_sentences_list[-1])

        # Now you can use the recognized_phrase variable as needed
        if recognized_phrase is not None:
            # Compute the Levenshtein distance between the two phrases
            distance = Levenshtein.distance(result_sentences_list[-1], recognized_phrase)

            # Calculate the similarity ratio
            max_length = max(len(result_sentences_list[-1]), len(recognized_phrase))
            similarity_ratio = 1 - (distance / max_length)

            similarity_threshold = 0.9  # Adjust the threshold as needed

            st.write("Similarity Ratio:", similarity_ratio)

            if similarity_ratio >= similarity_threshold:
                st.success("The recognized phrase is similar enough to the correct phrase.")
            else:
                st.error("The recognized phrase is not similar to the correct phrase.")

                st.write("Differences:")
                html = ""
                correct_words = result_sentences_list[-1].split()
                recognized_words = recognized_phrase.split()

                for word in correct_words:
                    if word in recognized_words:
                        html += f'<span style="color:white;">{word}</span> '
                    else:
                        html += f'<span style="color:red;">{word}</span> '

                st.markdown(html, unsafe_allow_html=True)

                differences = [word[2:] for word in difflib.ndiff(result_sentences_list[-1].split(), recognized_phrase.split()) if word[0] == '-']

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
                        
                        # Check if the new result_sentence is the same as the previous one
                        if result_sentence == prev_result_sentence:
                            st.write("The loop will break because the result_sentence repeated.")
                            break
                        # Append the new result_sentence to the list
                        result_sentences_list.append(result_sentence)
                        # Update the previous result_sentence
                        prev_result_sentence = result_sentence
                    else:
                        st.write(f"No sentence found containing '{target_word}'.")
                        # Break the loop if a certain condition is met
                        break

                    # Button to start the next iteration
                    if st.button("Start Next Iteration"):
                        # Set the instruction for the user to speak the next sentence containing the target word
                        if result_sentences_list:
                            target_word = rhymes[0] if rhymes else ""
                            next_target_sentence = find_sentence_with_word(target_word, texts)
                            instruction_text = f"Speak the phrase: {next_target_sentence}"
                            # Set the instruction for the user
                            instruction_text = "Speak the phrase: " + (result_sentences_list[-1] if result_sentences_list else texts[0])
                            st.write(instruction_text)
                            # Continue to the next iteration
                            continue
                        else:
                            st.write("Press the 'Start Next Iteration' button to continue.")
                            break


                   
