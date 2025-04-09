

"""This contains the text summarizer function to summarize, imports are in requirements.txt already
there
no true import errors
the text that is gotten from speech to text"""

# pylint: disable=import-error,unused-import
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# need to download NLTK data
nltk.download("punkt_tab")

# import this into the webapp and run it to summarize a given note once it has
# been converted from speech to text


def summarize_text(text, language, sentences_count):
    """Summarize the given text based on the LexRank Summarization which is supposed to be

    Better than LSA for shorter paragraphs will likely occur

    """
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    stemmer = Stemmer("english")

    summarizer = LexRankSummarizer(stemmer)

    summarizer.stop_words = get_stop_words(language)

    summary_array = []
    # 2 sentence summaries
    for sentence in summarizer(parser.document, sentences_count):
        summary_array.append(str(sentence))

    return " ".join(summary_array)


def summarize_text_access(text):
    """A getter to expose it easily for when it is imported, summary length and language all"""
    return summarize_text(text, language="english", sentences_count=1)


# this part is just for testing
def main():
    """put in some input and summarize it (for testing)"""
    summ = summarize_text_access(input("Enter text you want to summarize"))

    print("This is the summary: " + summ)


if __name__ == "__main__":
    main()
