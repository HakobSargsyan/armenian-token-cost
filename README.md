# What Armenian costs in an LLM

The same sentence costs a different number of tokens in different languages. Tokens are
what you pay for, what fills your context window, and what the model has to process — so
languages written in non-Latin scripts are measurably more expensive to work with.

This repository measures that gap for Armenian, with reproducible numbers.

## Headline result

Identical paragraph, same meaning, ~470–485 characters, measured with OpenAI's `tiktoken`:

| Language | GPT-4 / GPT-3.5 (`cl100k_base`) | GPT-4o and newer (`o200k_base`) |
| --- | --- | --- |
| English | 82 tokens — 1.00x | 82 tokens — 1.00x |
| Russian | 202 tokens — 2.46x | 104 tokens — 1.27x |
| **Armenian** | **873 tokens — 10.65x** | **147 tokens — 1.79x** |

Two things to take from this.

**The old generation was brutal.** On `cl100k_base`, Armenian cost more than ten times
English for the same content. A product serving Armenian text paid ten times the API bill,
fit a tenth as much into the same context window, and handed the model a sequence where
single words were shattered into dozens of fragments.

**The new generation is much better, but not equal.** `o200k_base` brings Armenian from
10.65x down to 1.79x — roughly a six-fold improvement. It is still nearly double English
and noticeably worse than Russian.

## Armenian script vs. Latin transliteration

Many Armenian speakers type transliterated Armenian (`barev, inchpes es`) out of habit.
Whether that is cheaper depends on the tokenizer and the text:

| Text | Tokenizer | Armenian script | Latin transliteration |
| --- | --- | --- | --- |
| Sentence | `cl100k_base` | 178 tokens | 37 tokens |
| Sentence | `o200k_base` | 29 tokens | **36 tokens** |
| Short greeting | `o200k_base` | 11 tokens | 7 tokens |

On the old tokenizer, transliteration was dramatically cheaper. On the current one that
advantage has largely disappeared, and for a full sentence the Armenian script is now
*cheaper* than writing the same thing in Latin letters. For very short phrases
transliteration still wins.

The practical takeaway: transliterating Armenian to save tokens is no longer a reliable
optimization on modern models. Measure your own text instead of assuming.

## Why it matters beyond the bill

- **Cost** — scales linearly with every call, on input and output both.
- **Context window** — fewer Armenian documents fit in the same window, which directly
  constrains RAG over Armenian-language sources.
- **Quality** — when a word is split into many fragments that carry no meaning on their
  own, the model has a harder time recovering its structure.
- **Latency** — more tokens means more to generate and more to process.

## Reproduce it

```bash
pip install -r requirements.txt
python tokencost.py
```

Options:

```bash
python tokencost.py --set paragraph      # one sample set
python tokencost.py --price 3.00         # your price per 1M input tokens
python tokencost.py --text "your text"   # measure your own
```

Full output is in [RESULTS.md](RESULTS.md). The parallel texts are in
[samples.json](samples.json) — add a language by adding a translation of the same content.

## Scope and honesty about it

These are **OpenAI tokenizers**, measured locally via `tiktoken`. Anthropic and Google do
not ship their tokenizers as open packages, so Claude and Gemini are not covered here;
their token counts for Armenian may differ. Contributions that measure other tokenizers
through their official counting APIs are welcome.

Georgian is included in the sentence set because it shows the same pattern — this is a
non-Latin-script problem, not an Armenian one specifically.

---

# Ինչ արժե հայերենը LLM-ի համար

Նույն նախադասությունը տարբեր լեզուներում արժենում է տարբեր քանակի token։ Token-ներն այն են,
ինչի համար վճարում ես, ինչով լցվում է context window-ը և ինչ պետք է մշակի մոդելը։ Հետևաբար
ոչ-լատինական այբուբենով գրվող լեզուներով աշխատելն ավելի թանկ է՝ չափելիորեն։

Այս repository-ն չափում է այդ տարբերությունը հայերենի համար՝ վերարտադրելի թվերով։

## Հիմնական արդյունքը

Նույն պարբերությունը, նույն իմաստով, ~470–485 նշան, չափված OpenAI-ի `tiktoken`-ով.

| Լեզու | GPT-4 / GPT-3.5 | GPT-4o և նորերը |
| --- | --- | --- |
| Անգլերեն | 82 token — 1.00x | 82 token — 1.00x |
| Ռուսերեն | 202 token — 2.46x | 104 token — 1.27x |
| **Հայերեն** | **873 token — 10.65x** | **147 token — 1.79x** |

Հին սերնդի tokenizer-ում հայերենն արժենում էր տասն անգամ ավելի, քան անգլերենը՝ նույն
բովանդակության համար։ Նոր սերնդում այդ ցուցանիշը 10.65x-ից իջել է 1.79x՝ մոտ վեց անգամ
բարելավում։ Բայց դեռ գրեթե կրկնակի ավելի է անգլերենից և ավելի վատ, քան ռուսերենը։

## Ինչու է սա կարևոր

- **Արժեք** — աճում է գծայնորեն՝ ամեն կանչի հետ։
- **Context window** — նույն պատուհանում ավելի քիչ հայերեն տեքստ է տեղավորվում, ինչը
  ուղղակիորեն սահմանափակում է հայերեն փաստաթղթերով RAG-ը։
- **Որակ** — երբ բառը բաժանվում է բազմաթիվ անիմաստ կտորների, մոդելին ավելի դժվար է
  վերականգնել կառուցվածքը։
- **Latency** — ավելի շատ token նշանակում է ավելի երկար մշակում։

## Վերարտադրել չափումը

```bash
pip install -r requirements.txt
python tokencost.py
```

Ամբողջական արդյունքը՝ [RESULTS.md](RESULTS.md)-ում։ Զուգահեռ տեքստերը՝ [samples.json](samples.json)-ում։

## Սահմանափակումներ

Սրանք **OpenAI-ի tokenizer-ներն** են։ Anthropic-ը և Google-ը իրենց tokenizer-ները բաց
փաթեթներով չեն տարածում, ուստի Claude-ը և Gemini-ն այստեղ ներառված չեն՝ նրանց թվերը
կարող են տարբերվել։

## License

MIT
