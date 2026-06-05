def generate_suggestions(df):

    suggestions = []

    text_data = " ".join(
        df["cleaned"]
    )

    negative_words = [
        "stress",
        "anxious",
        "sad",
        "tired",
        "lonely",
        "depressed",
        "fear"
    ]

    if any(
        word in text_data
        for word in negative_words
    ):

        suggestions.append(
            "Practice breathing exercises for 5-10 minutes daily."
        )

        suggestions.append(
            "Try reducing mental overload and take short breaks."
        )

    positive_count = len(
        df[df["sentiment"] == "Positive"]
    )

    negative_count = len(
        df[df["sentiment"] == "Negative"]
    )

    if positive_count > negative_count:

        suggestions.append(
            "Your emotional trend appears stable. Maintain healthy habits."
        )

    if negative_count > positive_count:

        suggestions.append(
            "Consider talking with close friends or family."
        )

    if len(suggestions) == 0:

        suggestions.append(
            "Maintain regular journaling and self-care."
        )

    return suggestions