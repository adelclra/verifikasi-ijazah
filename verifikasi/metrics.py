def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def compute_cer(ocr_text, reference_text):
    if not reference_text:
        return 0.0

    ocr_clean = ocr_text.strip().lower()
    ref_clean = reference_text.strip().lower()

    if ocr_clean == ref_clean:
        return 0.0

    distance = levenshtein_distance(ocr_clean, ref_clean)
    return distance / max(len(ref_clean), 1)


def compute_wer(ocr_text, reference_text):
    if not reference_text:
        return 0.0

    ocr_words = ocr_text.strip().lower().split()
    ref_words = reference_text.strip().lower().split()

    if ocr_words == ref_words:
        return 0.0

    distance = levenshtein_distance(ocr_words, ref_words)
    return distance / max(len(ref_words), 1)