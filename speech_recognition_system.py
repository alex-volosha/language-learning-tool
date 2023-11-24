import pandas as pd
import pronouncing
import speech_recognition as sr
import Levenshtein
import difflib

class SpeechRecognitionSystem:
    def __init__(self, texts, unique_word_dict):
        self.texts = texts
        self.unique_word_dict = unique_word_dict
        self.recognized_phrase = None
        self.recommend_sentences_list = [self.texts[0]]
        self.prev_recommend_sentence = ""

    def check_phrase(self, expected_phrase):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print(f"Speak the phrase: {expected_phrase}")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text.capitalize() + ".")

            capitalized_text = text.capitalize() + "."

            return capitalized_text

        except sr.UnknownValueError:
            print("Could not understand the speech.")
            return None
        except sr.RequestError as e:
            print("Request error:", e)
            return None

    def find_rhymes_in_list(self, word):
        rhymes = pronouncing.rhymes(word)
        rhymes_in_list = [rhyme for rhyme in rhymes if rhyme in self.unique_word_dict]
        return rhymes_in_list

    def find_sentence_with_word(self, target_word):
        target_word = target_word.lower()

        for sentence in self.texts:
            if target_word in sentence.lower():
                return sentence

        return None

    def print_differences(self, sentence1, sentence2):
        print("Differences (red is incorrect):")
        for word in difflib.ndiff(sentence1.split(), sentence2.split()):
            if word[0] == ' ':
                print(word[2:], end=' ')
            elif word[0] == '-':
                print(f'\033[91m{word[2:]}\033[0m', end=' ')

        differences = [word[2:] for word in difflib.ndiff(sentence1.split(), sentence2.split()) if word[0] == '-']
        print("\nIncorrect words:", differences)