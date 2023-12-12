import speech_recognition as sr
import streamlit as st
import Levenshtein
import difflib

# Initialize the Streamlit app
st.title("Speech Recognition App")

# The phrase that the user should speak
correct_phrase = "She had to abandon her old car and buy a new one."

# Function to check the phrase and return the recognized text
def check_phrase():
    with sr.Microphone() as source:
        st.write("Speak the phrase: " + correct_phrase)
        audio = recognizer.listen(source)

    try:
        # Recognize the speech using the Google Web Speech API
        text = recognizer.recognize_google(audio)
        st.write("You said: " + text.capitalize() + ".")
        
         # Add a dot at the end
        text += "."

        # Capitalize the first letter
        text = text.capitalize()


        # Check if the spoken phrase matches the correct phrase
        if correct_phrase.lower() == text.lower():
            st.success("You spoke the correct phrase!")
        else:
            st.error("You didn't speak the correct phrase. Please try again.")

        return text  # Return the recognized text

    except sr.UnknownValueError:
        st.warning("Could not understand the speech.")
        return None  # Return None if speech couldn't be recognized
    except sr.RequestError as e:
        st.error("Request error: {0}".format(e))
        return None  # Return None in case of a request error

# Create a button in Streamlit to trigger speech recognition
if st.button("Start Speech Recognition"):
    # Initialize the speech recognizer
    recognizer = sr.Recognizer()

    # Execute the function to check the phrase and store the recognized phrase
    recognized_phrase = check_phrase()

    # Now you can use the recognized_phrase variable as needed
    if recognized_phrase is not None:
        # Compute the Levenshtein distance between the two phrases
        distance = Levenshtein.distance(correct_phrase, recognized_phrase)

        # Calculate the similarity ratio
        max_length = max(len(correct_phrase), len(recognized_phrase))
        similarity_ratio = 1 - (distance / max_length)

        similarity_threshold = 0.8  # Adjust the threshold as needed

        #st.write("Levenshtein Distance:", distance)
        st.write("Similarity Ratio:", round(similarity_ratio, 2))

        if similarity_ratio >= similarity_threshold:
            st.success("The recognized phrase is similar enough to the correct phrase.")
        else:
            st.error("The recognized phrase is not similar to the correct phrase.")

            st.write("Differences:")
            html = ""
            correct_words = correct_phrase.split()
            recognized_words = recognized_phrase.split()

            for word in correct_words:
                if word in recognized_words:
                    html += f'<span style="color:white;">{word}</span> '
                else:
                    html += f'<span style="color:red;">{word}</span> '

            st.markdown(html, unsafe_allow_html=True)

