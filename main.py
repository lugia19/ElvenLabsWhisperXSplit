import string

import whisperx
import whisper
import elevenlabslib
import elevenlabslib.helpers
from pydub import AudioSegment

api_key = "API KEY HERE"
user = elevenlabslib.ElevenLabsUser(api_key)
voice = user.get_voices_by_name("Rachel")[0]

def generate_and_splice_text(quotedText, postText):
    """
    This function will generate two files: audio.mp3, with the full audio, and cut_audio.mp3, with only the quotedText

    :param quotedText: The text to be put in quotes.
    :param postText: The text after the quoted section that will be removed from the final audio file.
    """
    device = "cuda"
    audioFile = "audio.mp3"
    splicedAudioFile = "cut_audio.mp3"

    print(f'Text to be generated: "{quotedText}" {postText}')
    audioData = voice.generate_audio_bytes(f'"{quotedText}" {postText}')
    elevenlabslib.helpers.save_audio_bytes(audioData,audioFile,outputFormat="mp3")

    # transcribe with original whisper
    model = whisper.load_model("medium.en", device)
    result = model.transcribe(audioFile)

    # load alignment model and metadata
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

    # align whisper output
    result_aligned = whisperx.align(result["segments"], model_a, metadata, audioFile, device)
    print(result_aligned["word_segments"]) # after alignment

    #If all you're interested in is how to use whisperX to get the timestamps, you can stop here.



    #Now we need to identify the start and end of the sentence.

    #I assume whisper correctly identifies every word (besides the punctuation we stripped) else I will drive myself insane.
    #I also make the assumption that you haven't re-used the quoted sentence elsewhere word for word.

    quoteStartTime = 0.0
    quoteEndTime = 0.0

    #Effectively what this entire chunk of code does is just identify the portion of text that corresponds to the quotedText, to find the start and end times.


    #Get all the words and strip them of all punctuation and casing.
    quotedWords = list()
    for word in quotedText.lower().split(" "):
        strippedWord = word
        for char in string.punctuation:
            strippedWord = strippedWord.replace(char,"")
        quotedWords.append(strippedWord)

    word_segments_stripped = result_aligned["word_segments"]
    for wordSegment in word_segments_stripped:
        newText = wordSegment["text"].lower()
        for char in string.punctuation:
            newText = newText.replace(char, "")
        wordSegment["text"] = newText

    possibleStarts = list()

    for index, wordSegment in enumerate(word_segments_stripped):
        if wordSegment["text"] == quotedWords[0]:
            print("Possibly found the start?")
            possibleStarts.append(index)

    fullAudioSegment = AudioSegment.from_mp3(audioFile)

    for possibleStart in possibleStarts:
        print(f"Checking from {possibleStart}")
        counter = 0
        while \
                counter < len(quotedWords) \
                and possibleStart+counter < len(word_segments_stripped) \
                and word_segments_stripped[possibleStart+counter]["text"] == quotedWords[counter]:
            counter = counter+1

        if counter == len(quotedWords):
            print("Found our match.")
            quoteStartTime = word_segments_stripped[possibleStart]["start"]
            endIndex = possibleStart+len(quotedWords)-1
            if endIndex == len(word_segments_stripped):
                quoteEndTime = fullAudioSegment.duration_seconds
            else:
                quoteEndTime = word_segments_stripped[endIndex]["end"]
                endOffset = (word_segments_stripped[endIndex+1]["start"] - quoteEndTime)/2
                quoteEndTime += endOffset
            break
        else:
            print("Did not match the entire phrase.")

    print(f"Identified start time: {quoteStartTime}\nIdentified end time: {quoteEndTime}")

    #Use pydub to extract the section of audio.
    cutAudioSegment = fullAudioSegment[quoteStartTime*1000:quoteEndTime*1000]
    cutAudioSegment.export(splicedAudioFile, format="mp3")

    input("Done. Press Enter to exit.")


if __name__=="__main__":
    generate_and_splice_text("Don't test me!","she shouted angrily.")