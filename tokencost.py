#!/usr/bin/env python3
"""Measure how many tokens the same text costs in different languages.

Armenian script is tokenized far less efficiently than Latin script, which
means Armenian-language products pay more per API call, fit less text into the
same context window, and run slower -- for saying the same thing.

Usage:
    python tokencost.py                    # all sample sets, all encodings
    python tokencost.py --set paragraph    # one sample set
    python tokencost.py --price 3.00       # cost per 1M input tokens
    python tokencost.py --text "..."       # measure your own text
"""

import argparse
import json
import pathlib
import sys

try:
    import tiktoken
except ImportError:
    sys.exit("tiktoken is not installed. Run: pip install -r requirements.txt")

# OpenAI's two tokenizer generations. cl100k_base backs GPT-4 and GPT-3.5;
# o200k_base backs GPT-4o and later, and has much better non-Latin coverage.
ENCODINGS = [
    ("cl100k_base", "GPT-4 / GPT-3.5"),
    ("o200k_base", "GPT-4o and newer"),
]

LANG_NAMES = {
    "en": "English",
    "hy": "Armenian",
    "hy_latin": "Armenian (Latin)",
    "ru": "Russian",
    "ka": "Georgian",
    "es": "Spanish",
    "tr": "Turkish",
}

HERE = pathlib.Path(__file__).parent


def load_samples():
    with open(HERE / "samples.json", encoding="utf-8") as fh:
        return json.load(fh)


def report(title, texts, enc, price_per_m, note=None):
    baseline = len(enc.encode(texts["en"]))

    print(f"### {title}")
    if note:
        print(f"_{note}_\n")
    print("| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |")
    print("| --- | --- | --- | --- | --- | --- |")

    for code, text in texts.items():
        if code.startswith("_"):
            continue
        tokens = len(enc.encode(text))
        cost = tokens / 1_000_000 * price_per_m * 1_000
        print(
            f"| {LANG_NAMES.get(code, code)} | {len(text)} | {tokens} | "
            f"{tokens / len(text):.2f} | {tokens / baseline:.2f}x | ${cost:.3f} |"
        )
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", dest="sample_set", help="measure only this sample set")
    parser.add_argument("--price", type=float, default=3.00,
                        help="USD per 1M input tokens (default: 3.00)")
    parser.add_argument("--text", help="measure your own text instead of the samples")
    args = parser.parse_args()

    if args.text:
        for name, label in ENCODINGS:
            enc = tiktoken.get_encoding(name)
            tokens = enc.encode(args.text)
            print(f"{label:20} {len(tokens):6} tokens  "
                  f"({len(tokens) / max(len(args.text), 1):.2f} per character)")
        return

    samples = load_samples()
    if args.sample_set:
        if args.sample_set not in samples:
            sys.exit(f"Unknown set. Available: {', '.join(samples)}")
        samples = {args.sample_set: samples[args.sample_set]}

    for name, label in ENCODINGS:
        enc = tiktoken.get_encoding(name)
        print(f"\n## {label}  (`{name}`)\n")
        for set_name, texts in samples.items():
            report(set_name.capitalize(), texts, enc, args.price, texts.get("_note"))


if __name__ == "__main__":
    main()
