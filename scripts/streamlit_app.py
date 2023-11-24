# streamlit_app.py

import streamlit as st
import pandas as pd
import Levenshtein
import difflib
from speech_recognition_system_stremlit import SpeechRecognitionSystem

# Reading the text from the input folder
texts = pd.read_csv('data/sentences_test.csv')['text'].tolist()

# Reading the words from the input folder
unique_word_dict = pd.read_csv('data/unique_words.csv')['abandon'].tolist()

# Create an instance of the SpeechRecognitionSystem
speech_recognition_system = SpeechRecognitionSystem(texts, unique_word_dict)

# Streamlit app
st.title("Speech Recognition System")

# Use st.empty() to dynamically update the content
output_container = st.empty()

# Streamlit button to trigger the recognition
if st.button("Recognize Speech"):
    # Access the attribute through the instance, not the class itself
    speech_recognition_system.recognized_phrase = speech_recognition_system.check_phrase(speech_recognition_system.recommend_sentences_list[-1])

    if speech_recognition_system.recognized_phrase is not None:
        distance = Levenshtein.distance(speech_recognition_system.recommend_sentences_list[-1], speech_recognition_system.recognized_phrase)
        max_length = max(len(speech_recognition_system.recommend_sentences_list[-1]), len(speech_recognition_system.recognized_phrase))
        similarity_ratio = 1 - (distance / max_length)

        similarity_threshold = 0.9

        output_container.write("Similarity Ratio:", similarity_ratio)

        if similarity_ratio >= similarity_threshold:
            output_container.write("The recognized phrase is similar enough to the correct phrase.")

            if len(speech_recognition_system.recommend_sentences_list) < len(texts):
                next_target_sentence = texts[len(speech_recognition_system.recommend_sentences_list)]
                instruction_text = f"Speak the next phrase: {next_target_sentence}"
                speech_recognition_system.recommend_sentences_list.append(next_target_sentence)
            else:
                output_container.write("All sentences have been spoken. You can end the loop or perform another action.")
        else:
            output_container.write("The recognized phrase is not similar to the correct phrase.")

            speech_recognition_system.print_differences(speech_recognition_system.recommend_sentences_list[-1], speech_recognition_system.recognized_phrase)

            differences = [word[2:] for word in difflib.ndiff(speech_recognition_system.recommend_sentences_list[-1].split(), speech_recognition_system.recognized_phrase.split()) if word[0] == '-']
            output_container.write("Incorrect words:", differences)

            if differences:
                input_word = differences[0]
                rhymes = speech_recognition_system.find_rhymes_in_list(input_word)

                if rhymes:
                    output_container.write(f"Rhymes for '{input_word}' in the word list: {', '.join(rhymes)}")
                else:
                    output_container.write(f"No rhymes found for '{input_word}' in the word list.")
                    
                target_word = rhymes[0]
                recommend_sentence = speech_recognition_system.find_sentence_with_word(target_word)

                if recommend_sentence:
                    output_container.write(f"The first sentence containing '{target_word}': {recommend_sentence}")

                    if recommend_sentence == speech_recognition_system.prev_recommend_sentence:
                        output_container.write("The loop will break because the recommend_sentence repeated.")
                    else:
                        # Update the list and previous recommend_sentence
                        speech_recognition_system.recommend_sentences_list.append(recommend_sentence)
                        speech_recognition_system.prev_recommend_sentence = recommend_sentence
                else:
                    output_container.write(f"No sentence found containing '{target_word}'.")
            else:
                output_container.write("No differences found.")
