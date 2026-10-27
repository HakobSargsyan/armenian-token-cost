#!/usr/bin/env python3
"""Compare how different model families tokenize the same Armenian text.

tokencost.py measures OpenAI's two tokenizer generations. This script widens
that to the other major open tokenizers, because the choice of model -- not
just the choice of language -- decides what Armenian text costs.

Every family here ships a real, downloadable tokenizer, so every number below
is reproducible on your machine. Families without a public tokenizer are
listed at the end rather than estimated.

Usage:
    python familycompare.py                  # all families, all sample sets
    python familycompare.py --set paragraph  # one sample set
    python familycompare.py --text "..."     # measure your own text
    python familycompare.py --price 3.00     # cost per 1M input tokens
"""

import argparse
import json
import pathlib
import sys

try:
    import tiktoken
except ImportError:
    sys.exit("tiktoken is not installed. Run: ./venv/bin/pip install -r requirements.txt")

try:
    from tokenizers import Tokenizer
except ImportError:
    sys.exit("tokenizers is not installed. Run: ./venv/bin/pip install -r requirements.txt")

# One entry per tokenizer family.
#   kind "tiktoken" -> a local tiktoken encoding
#   kind "hf"       -> a tokenizer.json pulled from the Hugging Face Hub
# Where Meta's and Google's own repos are gated behind a licence click, we use
# a byte-identical community mirror so the script runs without a HF token.
FAMILIES = [
    ("GPT-4 / GPT-3.5", "tiktoken", "cl100k_base",
     "OpenAI's previous generation"),
    ("GPT-4o and newer", "tiktoken", "o200k_base",
     "OpenAI's current generation"),
    ("Llama 3.1", "hf", "NousResearch/Meta-Llama-3.1-8B",
     "ungated mirror of meta-llama/Llama-3.1-8B"),
    ("Mistral v0.3", "hf", "mistralai/Mistral-7B-Instruct-v0.3",
     "also backs Mixtral"),
    ("Gemma 2", "hf", "unsloth/gemma-2-9b",
     "ungated mirror; the closest public relative of Gemini's tokenizer, not Gemini itself"),
    ("Qwen 2.5", "hf", "Qwen/Qwen2.5-7B",
     "Alibaba; also backs many fine-tunes"),
    ("DeepSeek-V3", "hf", "deepseek-ai/DeepSeek-V3",
     "DeepSeek's current tokenizer"),
]

# Families whose tokenizer is not published. Counting their tokens needs a
# billed API round-trip, so they are named here instead of guessed at.
NO_PUBLIC_TOKENIZER = [
    ("Claude", "Anthropic does not publish a tokenizer for Claude 3 and later. "
               "Token counts are available only through the API's count_tokens endpoint."),
    ("Gemini", "Google does not publish Gemini's tokenizer. The Gemma 2 row above is a "
               "relative of it, not a substitute -- treat it as an indication, not a measurement."),
]

HERE = pathlib.Path(__file__).parent


def load_samples():
    with open(HERE / "samples.json", encoding="utf-8") as fh:
        return json.load(fh)


# Armenian block: uppercase Ա-Ֆ and lowercase ա-ֆ.
ARMENIAN = {chr(c) for c in range(0x531, 0x557)} | {chr(c) for c in range(0x561, 0x587)}


def _byte_decoder():
    """The GPT-2 byte-to-unicode table, inverted.

    Byte-level BPE vocabularies store each byte as a printable stand-in
    character, so 'ա' is filed under 'Õ¡'. To ask what a token really spells we
    have to map those stand-ins back to bytes first.
    """
    printable = (list(range(ord("!"), ord("~") + 1))
                 + list(range(ord("\xa1"), ord("\xac") + 1))
                 + list(range(ord("\xae"), ord("\xff") + 1)))
    stand_ins, extra = printable[:], 0
    for byte in range(256):
        if byte not in printable:
            printable.append(byte)
            stand_ins.append(256 + extra)
            extra += 1
    return {chr(c): b for b, c in zip(printable, stand_ins)}


BYTE_DECODER = _byte_decoder()


def _as_text(token):
    """Read a byte-level token back into the text it spells, or None."""
    try:
        return bytes(BYTE_DECODER[ch] for ch in token).decode("utf-8")
    except (KeyError, UnicodeDecodeError):
        return None


def load_family(kind, ident):
    """Return count(text) -> int, the vocabulary size, and the vocab as text."""
    if kind == "tiktoken":
        enc = tiktoken.get_encoding(ident)
        strings = []
        for token in enc._mergeable_ranks:
            try:
                strings.append(token.decode("utf-8"))
            except UnicodeDecodeError:          # a bare byte, spells nothing
                pass
        return (lambda text: len(enc.encode(text))), enc.n_vocab, strings

    tok = Tokenizer.from_pretrained(ident)
    keys = list(tok.get_vocab())
    # SentencePiece vocabs (Gemma, Mistral) already hold real characters;
    # byte-level ones (Llama, Qwen, DeepSeek) need decoding. Try both and keep
    # whichever reading actually finds Armenian.
    decoded = [t for t in (_as_text(k) for k in keys) if t]
    strings = decoded if _armenian_in(decoded) > _armenian_in(keys) else keys
    count = lambda text: len(tok.encode(text, add_special_tokens=False).ids)
    return count, tok.get_vocab_size(), strings


def _armenian_in(strings):
    return sum(1 for s in strings if s and any(ch in ARMENIAN for ch in s))


def coverage(strings):
    """How much of a vocabulary is spent on Armenian.

    `whole` counts every token containing Armenian; `chunks` counts only those
    spelling two or more Armenian characters, which are the ones that actually
    buy compression -- a vocabulary of single letters still spells a word one
    token at a time.
    """
    armenian = [s for s in strings if s and any(ch in ARMENIAN for ch in s)]
    chunks = [s for s in armenian
              if sum(1 for ch in s if ch in ARMENIAN) >= 2]
    longest = max(armenian, key=lambda s: sum(1 for ch in s if ch in ARMENIAN),
                  default="")
    return len(armenian), len(chunks), longest.strip()


def load_all():
    """Load every family, skipping any that cannot be fetched."""
    loaded, skipped = [], []
    for label, kind, ident, note in FAMILIES:
        try:
            count, vocab, strings = load_family(kind, ident)
        except Exception as exc:                      # offline, gated, renamed
            skipped.append((label, ident, f"{type(exc).__name__}: {exc}"))
            continue
        loaded.append((label, ident, note, count, vocab, strings))
    return loaded, skipped


def report(title, texts, families, price_per_m, note=None):
    """One sample set, every family as a row."""
    print(f"### {title}")
    if note:
        print(f"_{note}_\n")
    print("| Family | Vocab | Armenian tokens | English tokens | Multiplier "
          "| Tokens/char | Cost / 1k calls |")
    print("| --- | --- | --- | --- | --- | --- | --- |")

    hy, en = texts["hy"], texts["en"]
    for label, _ident, _note, count, vocab, _strings in families:
        n_hy, n_en = count(hy), count(en)
        cost = n_hy / 1_000_000 * price_per_m * 1_000
        print(f"| {label} | {vocab:,} | {n_hy} | {n_en} | {n_hy / n_en:.2f}x "
              f"| {n_hy / len(hy):.2f} | ${cost:.3f} |")
    print()


def spread(texts, families):
    """The headline: how far apart the best and worst family are."""
    counts = [(count(texts["hy"]), label)
              for label, _i, _n, count, _v, _s in families]
    best_n, best = min(counts)
    worst_n, worst = max(counts)
    print(f"**Spread:** the same Armenian text costs {worst_n} tokens in {worst} "
          f"and {best_n} in {best} -- {worst_n / best_n:.1f}x apart, "
          f"for identical input.\n")


def report_coverage(texts, families):
    """Why the families rank the way they do.

    Vocabulary size turns out not to predict the Armenian cost. What predicts
    it is how many multi-character Armenian tokens a vendor chose to spend
    that vocabulary on.
    """
    print("### Why: Armenian coverage in the vocabulary\n")
    print("| Family | Vocab | Armenian tokens | Multi-char | Longest Armenian token "
          "| Paragraph cost |")
    print("| --- | --- | --- | --- | --- | --- |")

    rows = []
    for label, _ident, _note, count, vocab, strings in families:
        whole, chunks, longest = coverage(strings)
        rows.append((count(texts["hy"]), label, vocab, whole, chunks, longest))

    for cost, label, vocab, whole, chunks, longest in sorted(rows, reverse=True):
        shown = f"`{longest}`" if longest else "none"
        print(f"| {label} | {vocab:,} | {whole:,} | {chunks:,} | {shown} "
              f"| {cost} tokens |")
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", dest="sample_set", help="measure only this sample set")
    parser.add_argument("--price", type=float, default=3.00,
                        help="USD per 1M input tokens (default: 3.00)")
    parser.add_argument("--text", help="measure your own text instead of the samples")
    args = parser.parse_args()

    families, skipped = load_all()
    if not families:
        sys.exit("No tokenizer could be loaded. Check your network connection.")

    if args.text:
        for label, _ident, _note, count, vocab, _strings in families:
            n = count(args.text)
            print(f"{label:20} {n:6} tokens  "
                  f"({n / max(len(args.text), 1):.2f} per character)")
        return

    samples = load_samples()
    if args.sample_set:
        if args.sample_set not in samples:
            sys.exit(f"Unknown set. Available: {', '.join(samples)}")
        samples = {args.sample_set: samples[args.sample_set]}

    print("## Armenian across tokenizer families\n")
    if "paragraph" in samples:
        spread(samples["paragraph"], families)

    for set_name, texts in samples.items():
        if set_name == "pairs":           # pairs has no top-level hy/en keys
            continue
        report(set_name.capitalize(), texts, families, args.price, texts.get("_note"))

    if "paragraph" in samples:
        report_coverage(samples["paragraph"], families)

    print("### What each row is\n")
    for label, ident, note, _count, _vocab, _strings in families:
        suffix = f" -- {note}" if note else ""
        print(f"- **{label}** — `{ident}`{suffix}")
    print()

    print("### Not measured\n")
    for label, why in NO_PUBLIC_TOKENIZER:
        print(f"- **{label}** — {why}")
    print()

    if skipped:
        print("### Could not be loaded in this run\n")
        for label, ident, why in skipped:
            print(f"- **{label}** (`{ident}`) — {why}")
        print()


if __name__ == "__main__":
    main()
