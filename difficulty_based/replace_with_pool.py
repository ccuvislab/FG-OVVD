import json
import random
import spacy
import re

# Load the SpaCy English model for tokenization and POS tagging
nlp = spacy.load("en_core_web_sm")

# Word pools for different parts of speech (verbs, adjectives, nouns)
# These pools contain possible words that can replace original words in the captions
VERB_POOL = [
    "parked", "driving", "displayed", "speeds", "racing", "accelerating", "climbing",
    "towing", "passing", "overtaking", "braking", "gliding", "drifting", "idling",
    "positioned", "standing", "resting", "showcasing", "maneuvering", "stopping",
    "sliding", "zooming", "lurking", "posing", "revving", "charging", "skidding", "cruising"
]

ADJECTIVE_POOL = [
    "blue", "red", "green", "yellow", "white", "gray", "orange", "brown", "black", "gold", "purple", "pink",
    "bronze", "chrome", "matte", "graphite", "small", "compact", "tiny", "narrow", "slim", "mini",
    "bulky", "rugged", "spacious", "oversized", "sleek", "boxy", "plain", "dull", "bright", "dim",
    "shadowy", "faint", "foggy", "luxurious", "modern", "classic", "clean", "tinted", "shiny", "sporty",
    "aggressive", "soft", "hard", "sharp", "messy", "glossy", "decorated", "faded", "glowing", "dusty",
    "vintage", "elegant", "streamlined", "noisy", "silent", "colorful", "reflective", "angular",
    "dynamic", "curvy", "blocky", "striped", "powerful", "rounded", "sophisticated"
]

NOUN_POOL = [
    "sedan", "SUV", "hatchback", "convertible", "pickup", "van", "wagon", "coupe", "minivan", "truck", "vehicle", "automobile", "car",
    "rims", "hubs", "tires", "spokes", "windows", "windshield", "glass", "panes", "screens", "grille", "bumper", "hood", "mesh",
    "lamps", "lights", "beams", "bulbs", "roof", "top", "canopy", "pipes", "vents", "outlets", "panel", "gate", "entrance",
    "registration", "plate", "tag", "taillights", "indicators", "signals", "headlights", "door", "mirror", "trunk", "engine",
    "dashboard", "seat", "steering", "sunroof", "wheelbase", "frame", "fender", "spoiler", "badge", "logo", "garage", "alley",
    "building", "sign", "highway", "road", "parking", "lot", "showroom", "background", "exhaust", "street", "lane", "trailer",
    "window", "light", "grill", "panel", "display", "hall", "event", "flag", "object", "surface", "ground",
    "intersection", "driveway", "asphalt", "terrain", "track", "interior", "skyline"
]

# This function performs word replacement based on the part of speech (POS)
# It chooses a word from the corresponding pool (VERB, ADJ, NOUN)
def replace_word(original, pos):
    if pos == "ADJ":
        pool = ADJECTIVE_POOL  # Adjectives are replaced using the ADJECTIVE_POOL
    elif pos == "NOUN":
        pool = NOUN_POOL  # Nouns are replaced using the NOUN_POOL
    elif pos == "VERB":
        pool = VERB_POOL  # Verbs are replaced using the VERB_POOL
    else:
        return None  # Return None if it's not one of the valid parts of speech
    options = [w for w in pool if w != original.lower()]  # Avoid replacing with the original word
    return random.choice(options) if options else None  # Randomly choose a replacement word

# This function ensures the replacement is safe and doesn't break the sentence structure
# It uses regular expressions to replace only the target word without affecting others
def safe_replace(text, target, replacement):
    pattern = r'\b' + re.escape(target) + r'\b'
    return re.sub(pattern, replacement, text, count=1, flags=re.IGNORECASE)

# This function generates negative samples by replacing words in the caption.
# By default, it replaces 2 words (medium level), but you can modify it to replace more or fewer words.
def generate_negatives_spacy(caption, n=10):
    protected_phrases = ["in front of"]  # List of phrases to protect from being replaced
    candidates = set()  # Set to store unique generated negative captions
    lower_caption = caption.lower()  # Convert the caption to lowercase for easier matching

    # Identify the spans of protected phrases in the caption
    protected_spans = []
    for phrase in protected_phrases:
        idx = lower_caption.find(phrase)
        if idx != -1:
            protected_spans.append((idx, idx + len(phrase)))

    # Function to check if a word is within a protected phrase
    def is_protected(start, end):
        return any(p_start <= start < p_end or p_start < end <= p_end for p_start, p_end in protected_spans)

    # This loop generates the required number of negative samples
    while len(candidates) < n:
        doc = nlp(caption)  # Tokenize the caption
        # Select valid tokens that are adjectives, nouns, or verbs, excluding protected ones
        valid_tokens = [
            token for token in doc
            if token.pos_ in {"ADJ", "NOUN", "VERB"} and not is_protected(token.idx, token.idx + len(token))
        ]
        if len(valid_tokens) < 2:
            break  # Stop if there are not enough valid tokens
        selected = random.sample(valid_tokens, 2)  # Randomly select 2 words to replace
        modified = caption  # Start with the original caption
        used = set()  # Set to track words that have already been replaced

        # Perform the replacements
        for token in selected:
            word = token.text
            pos = token.pos_
            if word.lower() in used:
                continue  # Skip if the word has already been replaced
            replacement = replace_word(word, pos)  # Get a replacement for the word
            if replacement:
                modified = safe_replace(modified, word, replacement)  # Replace the word in the caption
                used.add(word.lower())  # Track the replaced word

        # Only add the modified caption if it's different from the original and not a duplicate
        if modified != caption and modified not in candidates:
            candidates.add(modified)

    return list(candidates)

# Main function to process input and output paths, and generate negative samples for the dataset
def main():
    input_path = "/path/to/your/input_data.json"  # Set the input file path here
    output_path = "/path/to/your/output_data.json"  # Set the output file path here

    with open(input_path, "r", encoding="utf-8") as f:
        data = [json.loads(line.strip()) for line in f if line.strip()]

    # Generate negative samples with 2 word replacements by default (this can be adjusted)
    for item in data:
        item["medium_negatives"] = generate_negatives_spacy(item["caption"], n=10)

    # Write the updated data with the generated negative samples
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Medium negatives (2-word changes) saved to: {output_path}")

if __name__ == "__main__":
    main()
