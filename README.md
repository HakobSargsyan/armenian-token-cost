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

## Mixed content: what real data looks like

The headline number comes from pure prose, but real payloads are rarely pure prose. Logs,
tickets and API requests are mostly ASCII — keys, IDs, timestamps, enum values, punctuation —
and that scaffolding tokenizes identically in both languages. The Armenian penalty applies
only to the natural-language fraction.

Measured on `o200k_base`:

| Payload | Armenian | English | Multiplier |
| --- | --- | --- | --- |
| Support ticket (English keys, Armenian values) | 123 | 111 | **1.11x** |
| Log line (Armenian message) | 44 | 34 | **1.29x** |
| Armenian prose with English tech terms | 60 | 42 | **1.43x** |
| Fully Armenian prose | 62 | 42 | **1.48x** |

So for cost modeling, do not multiply the whole payload. Apply the multiplier to the
natural-language fraction: ticket and log pipelines land near 1.1–1.3x, while document
pipelines, which are nearly all prose, approach the full rate.

One finding worth noting separately: on `cl100k_base`, Armenian prose written with English
technical terms cost 230 tokens against 338 for the fully-Armenian version — code-switching
saved a third. On `o200k_base` that gap is gone (60 against 62). Mixing in English used to be
a real optimization and no longer is.

These pairs are faithful translations rather than length-matched strings, so treat the ratios
as indicative. The length-matched comparison is the paragraph set above.

## Which model is cheapest for Armenian

The sections above compare languages inside OpenAI's tokenizers. This one compares
tokenizers against each other, on the same Armenian paragraph. Every family below ships a
real, downloadable tokenizer, so every number is reproducible locally — no API key:

| Family | Vocab | Armenian tokens | vs English | Cost / 1k calls at $3/1M |
| --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 873 | 10.65x | $2.619 |
| Llama 3.1 | 128,256 | 786 | 9.59x | $2.358 |
| Mistral v0.3 | 32,768 | 534 | 6.28x | $1.602 |
| Qwen 2.5 | 151,665 | 476 | 5.80x | $1.428 |
| Gemma 2 | 256,000 | 273 | 3.29x | $0.819 |
| DeepSeek-V3 | 128,815 | 273 | 3.33x | $0.819 |
| **GPT-4o and newer** | 200,019 | **147** | **1.79x** | **$0.441** |

Identical input, 5.9x apart in price. Choosing Llama 3.1 over GPT-4o for an
Armenian-language product costs 5.3x more tokens per call before a single word of the
model's own output.

### Why: vocabulary size does not predict this

The obvious explanation would be that bigger vocabularies tokenize Armenian better. The
data says otherwise. Mistral has **a quarter** of Llama 3.1's vocabulary and spends 32%
fewer tokens on the same Armenian text. Gemma has the largest vocabulary in the table and
still needs 86% more tokens than GPT-4o.

What does predict the cost is how much of the vocabulary each vendor chose to spend on
Armenian — specifically on *multi-character* Armenian tokens, the ones that actually buy
compression. A vocabulary holding single Armenian letters still spells a word one token at
a time:

| Family | Vocab | Armenian tokens in vocab | Multi-char | Longest Armenian token | Paragraph cost |
| --- | --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 0 | 0 | none | 873 |
| Llama 3.1 | 128,256 | 1 | 0 | `ա` | 786 |
| Mistral v0.3 | 32,768 | 28 | 0 | `ւ` | 534 |
| Qwen 2.5 | 151,665 | 72 | 0 | `Ց` | 476 |
| DeepSeek-V3 | 128,815 | 189 | 118 | `ությունը` | 273 |
| Gemma 2 | 256,000 | 231 | 118 | `ագրություններ` | 273 |
| GPT-4o and newer | 200,019 | 1,726 | 1,578 | `հնարավորություն` | 147 |

The ordering is exact: sort the families by multi-character Armenian coverage and you have
sorted them by Armenian cost. Llama 3.1 allocated 128,256 tokens of vocabulary and gave
Armenian exactly one of them, so it falls back to spelling Armenian out byte by byte.
GPT-4o holds 1,578 multi-character Armenian tokens, including whole words like
`հնարավորություն` — one token for a 15-character word.

This is a decision, not a property of the language. Armenian is expensive in a model
because somebody allocated the vocabulary that way.

Full output: [FAMILIES.md](FAMILIES.md).

### Claude and Gemini

Neither tokenizer is published, so neither can be loaded from a file like the rows above.

**Claude can still be measured, through the API.** Anthropic's `count_tokens` endpoint is
not billed for tokens — only rate limited — so adding Claude costs nothing beyond having a
key. `familycompare.py` includes it automatically when `ANTHROPIC_API_KEY` is set:

```bash
./venv/bin/pip install anthropic
export ANTHROPIC_API_KEY=...
./venv/bin/python familycompare.py          # Claude appears as a row
./venv/bin/python familycompare.py --no-claude   # or skip it
```

Two details worth knowing if you do this. The endpoint counts a whole request, so each
call carries a fixed message wrapper; this script measures that overhead once and
subtracts it, so its Claude numbers line up with the local tokenizers instead of being
inflated by a constant. And **`tiktoken` is not a usable proxy for Claude** — Anthropic's
own documentation puts it at 15–20% under on ordinary text, and further off on code and
non-English input. Do not estimate Claude's Armenian cost from the GPT rows.

**Gemini cannot be measured here at all.** Google publishes neither the tokenizer nor a
free counting endpoint. Gemma 2 is its closest public relative, not a stand-in — read that
row as an indication, not a measurement.

## Why it matters beyond the bill

- **Cost** — scales linearly with every call, on input and output both.
- **Context window** — fewer Armenian documents fit in the same window, which directly
  constrains RAG over Armenian-language sources.
- **Quality** — when a word is split into many fragments that carry no meaning on their
  own, the model has a harder time recovering its structure.
- **Latency** — more tokens means more to generate and more to process.

## Reproduce it

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python tokencost.py
```

A virtual environment is required on Debian, Ubuntu and other distributions that mark the
system Python as externally managed (PEP 668). Elsewhere, `pip install -r requirements.txt`
and `python tokencost.py` work directly.

Options:

```bash
./venv/bin/python tokencost.py --set pairs       # one sample set
./venv/bin/python tokencost.py --price 3.00      # your price per 1M input tokens
./venv/bin/python tokencost.py --text "your text"  # measure your own
```

To compare model families instead of languages:

```bash
./venv/bin/python familycompare.py                   # every family, every set
./venv/bin/python familycompare.py --set paragraph   # one sample set
./venv/bin/python familycompare.py --text "your text"
```

The first run downloads six tokenizer files from the Hugging Face Hub (a few MB, cached
afterwards) and needs no account or token. Families that cannot be reached are listed as
skipped rather than silently dropped.

Full output is in [RESULTS.md](RESULTS.md). The texts are in [samples.json](samples.json):
`paragraph`, `sentence` and `greeting` hold the same content in many languages, and `pairs`
holds realistic Armenian/English payloads. Add a language by adding a translation.

## Scope and honesty about it

`tokencost.py` measures **OpenAI tokenizers** via `tiktoken`. `familycompare.py` adds
Llama, Mistral, Gemma, Qwen and DeepSeek, loaded from their published `tokenizer.json`
files. Where a vendor gates its own repository behind a licence click, a byte-identical
community mirror is used so the script runs without credentials; the exact repository for
every row is printed in the output.

**Claude is measured only if you supply a key**, through `count_tokens` (free, rate
limited); without one it is reported as unmeasured rather than estimated. **Gemini is not
measured at all** — no published tokenizer, no free counting endpoint. Neither is ever
approximated from the GPT numbers: `tiktoken` is 15–20% under for Claude on ordinary text
and worse on non-English input.

A tokenizer is not a model. These numbers say what Armenian text *costs*; they say nothing
about how well a model *understands* Armenian. The cheapest tokenizer is not automatically
the best choice.

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

## Ո՞ր մոդելն է ամենաէժանը հայերենի համար

Վերևի բաժինները համեմատում են լեզուները OpenAI-ի tokenizer-ների ներսում։ Սա համեմատում է
tokenizer-ները միմյանց հետ՝ նույն հայերեն պարբերությամբ։ Բոլոր թվերը վերարտադրելի են
տեղում, առանց API բանալու.

| Ընտանիք | Vocab | Հայերեն token | vs անգլերեն |
| --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 873 | 10.65x |
| Llama 3.1 | 128,256 | 786 | 9.59x |
| Mistral v0.3 | 32,768 | 534 | 6.28x |
| Qwen 2.5 | 151,665 | 476 | 5.80x |
| Gemma 2 | 256,000 | 273 | 3.29x |
| DeepSeek-V3 | 128,815 | 273 | 3.33x |
| **GPT-4o և նորերը** | 200,019 | **147** | **1.79x** |

Նույն մուտքը՝ 5.9 անգամ տարբերություն։

### Ինչու. vocab-ի չափը ոչինչ չի բացատրում

Mistral-ի բառապաշարը Llama 3.1-ի **քառորդն** է, բայց նույն հայերեն տեքստի վրա 32%-ով քիչ
token է ծախսում։ Gemma-ն ունի աղյուսակի ամենամեծ vocab-ը և դեռ 86%-ով ավելի շատ token է
պահանջում, քան GPT-4o-ն։

Իրական բացատրությունը այն է, թե vocab-ի որ մասն է տրվել հայերենին՝ մասնավորապես
**մի քանի տառանոց** հայերեն token-ներին։ Մեկ տառանոց token-ներով բառը դեռ տառ-առ-տառ է
գրվում.

| Ընտանիք | Հայերեն token vocab-ում | Մի քանի տառանոց | Ամենաերկարը | Պարբերության արժեքը |
| --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 0 | 0 | չկա | 873 |
| Llama 3.1 | 1 | 0 | `ա` | 786 |
| Mistral v0.3 | 28 | 0 | `ւ` | 534 |
| Qwen 2.5 | 72 | 0 | `Ց` | 476 |
| DeepSeek-V3 | 189 | 118 | `ությունը` | 273 |
| Gemma 2 | 231 | 118 | `ագրություններ` | 273 |
| GPT-4o և նորերը | 1,726 | 1,578 | `հնարավորություն` | 147 |

Հերթականությունը ճշգրիտ է՝ դասավորիր ընտանիքները ըստ հայերենի ծածկույթի, և ստացել ես
նույն դասավորությունը ըստ արժեքի։ Llama 3.1-ը բաշխել է 128,256 token և հայերենին տվել
ուղիղ մեկը, ուստի մնացածը գրում է բայթ-առ-բայթ։ GPT-4o-ն ունի 1,578 բազմատառ հայերեն
token, ներառյալ ամբողջական բառեր՝ `հնարավորություն` մեկ token-ով, 15 նշան։

Սա որոշում է, ոչ թե լեզվի հատկություն։ Հայերենը թանկ է, որովհետև ինչ-որ մեկը vocab-ը
այդպես է բաշխել։

Ամբողջական արդյունքը՝ [FAMILIES.md](FAMILIES.md)։

## Ինչու է սա կարևոր

- **Արժեք** — աճում է գծայնորեն՝ ամեն կանչի հետ։
- **Context window** — նույն պատուհանում ավելի քիչ հայերեն տեքստ է տեղավորվում, ինչը
  ուղղակիորեն սահմանափակում է հայերեն փաստաթղթերով RAG-ը։
- **Որակ** — երբ բառը բաժանվում է բազմաթիվ անիմաստ կտորների, մոդելին ավելի դժվար է
  վերականգնել կառուցվածքը։
- **Latency** — ավելի շատ token նշանակում է ավելի երկար մշակում։

## Վերարտադրել չափումը

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python tokencost.py        # լեզուները՝ OpenAI-ի tokenizer-ներում
./venv/bin/python familycompare.py    # մոդելների ընտանիքները՝ իրար դեմ
```

Virtual environment-ը պարտադիր է Debian/Ubuntu-ի վրա (PEP 668)։

Ամբողջական արդյունքը՝ [RESULTS.md](RESULTS.md)-ում։ Զուգահեռ տեքստերը՝ [samples.json](samples.json)-ում։

## Սահմանափակումներ

`tokencost.py`-ն չափում է **OpenAI-ի tokenizer-ները**։ `familycompare.py`-ն ավելացնում է
Llama, Mistral, Gemma, Qwen և DeepSeek՝ իրենց հրապարակված `tokenizer.json` ֆայլերից։

**Claude-ը** չափվում է միայն քո API բանալիով՝ `count_tokens` endpoint-ով, որը token-ի
համար գումար չի գանձում։ Բանալի դնելուց հետո ավտոմատ հայտնվում է աղյուսակում։

**Gemini-ն ընդհանրապես չափելի չէ** այստեղ՝ ո՛չ tokenizer, ո՛չ անվճար հաշվիչ։ Gemma 2-ը
ամենամոտ ազգականն է, բայց ոչ փոխարինողը։

Եւ կարևորը՝ **tiktoken-ը Claude-ի համար պիտանի չէ**։ Anthropic-ի փաստաթղթերով՝ սովորական
տեքստի վրա 15-20%-ով քիչ է ցույց տալիս, ոչ-անգլերենի վրա՝ ավելի շատ։ Ուրեմն GPT-ի թվերից
Claude-ի արժեքը չի կարելի ենթադրել։

Tokenizer-ը մոդել չէ։ Այս թվերը ցույց են տալիս, թե հայերենը որքան **արժե**, ոչ թե որքան
լավ է մոդելը հայերեն **հասկանում**։ Ամենաէժան tokenizer-ը ավտոմատ լավագույն ընտրությունը չէ։

## License

MIT
