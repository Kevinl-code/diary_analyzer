from collections import Counter
import pandas as pd

def get_common_words(df):

    all_words = " ".join(
        df["cleaned"]
    ).split()

    common_words = Counter(
        all_words
    ).most_common(10)

    return common_words

def generate_word_dataframe(common_words):

    word_df = pd.DataFrame(
        common_words,
        columns=["Word", "Count"]
    )

    return word_df