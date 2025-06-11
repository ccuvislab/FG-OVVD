# 📁 Difficulty-based Captions

## ✅ Positive Captions

- `test_caption_results_15words.json`: Ground-truth captions used as reference

## ❌ Negative Captions

- `test_caption_results_with_trivial_negatives.json`: Trivial – unrelated captions from other images
- `test_caption_results_15words_easy_negatives_template.json`: Easy – 3 word replacements
- `test_caption_results_15words_medium_negatives_template.json`: Medium – 2 word replacements
- `test_caption_results_15words_hard_negatives.json`: Hard – 1 word replacement (high semantic confusion)

## 🧠 Word Replacement Logic

- See: `replace_with_pool.py`
