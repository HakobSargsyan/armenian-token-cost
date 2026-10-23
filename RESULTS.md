
## GPT-4 / GPT-3.5  (`cl100k_base`)

### Paragraph
_Same meaning, same approximate length (~470-485 characters) in every language._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 470 | 82 | 0.17 | 1.00x | $0.246 |
| Armenian | 485 | 873 | 1.80 | 10.65x | $2.619 |
| Russian | 471 | 202 | 0.43 | 2.46x | $0.606 |

### Sentence
_One parallel sentence, used to compare Armenian script against Latin transliteration._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 78 | 12 | 0.15 | 1.00x | $0.036 |
| Armenian | 95 | 178 | 1.87 | 14.83x | $0.534 |
| Armenian (Latin) | 94 | 37 | 0.39 | 3.08x | $0.111 |
| Russian | 77 | 32 | 0.42 | 2.67x | $0.096 |
| Spanish | 101 | 21 | 0.21 | 1.75x | $0.063 |
| Turkish | 76 | 32 | 0.42 | 2.67x | $0.096 |
| Georgian | 81 | 151 | 1.86 | 12.58x | $0.453 |

### Greeting
_Everyday short phrase. Short inputs are where per-language overhead hurts most._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 19 | 6 | 0.32 | 1.00x | $0.018 |
| Armenian | 17 | 31 | 1.82 | 5.17x | $0.093 |
| Armenian (Latin) | 18 | 8 | 0.44 | 1.33x | $0.024 |
| Russian | 17 | 8 | 0.47 | 1.33x | $0.024 |

### Mixed content
_Realistic mixed-content payloads. Each pair is a faithful translation, NOT length-matched, so ratios are indicative rather than precise. Real-world data is rarely pure prose: structured fields, keys and IDs are ASCII and tokenize identically in both languages, so the Armenian penalty applies only to the natural-language fraction._

| Payload | Armenian tokens | English tokens | Multiplier | HY chars |
| --- | --- | --- | --- | --- |
| support ticket | 388 | 111 | 3.50x | 364 |
| log line | 100 | 34 | 2.94x | 116 |
| code switched prose | 230 | 43 | 5.35x | 184 |
| fully armenian prose | 338 | 43 | 7.86x | 181 |

- **support ticket** — Support ticket: English keys and metadata, natural-language fields in each language.
- **log line** — Structured log line: ASCII prefix dominates, only the message is translated.
- **code switched prose** — How Armenian engineers actually write: Armenian grammar, English technical terms. Compare against fully_armenian below.
- **fully armenian prose** — The same content with technical terms translated into Armenian. Isolates the cost of avoiding English loanwords.


## GPT-4o and newer  (`o200k_base`)

### Paragraph
_Same meaning, same approximate length (~470-485 characters) in every language._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 470 | 82 | 0.17 | 1.00x | $0.246 |
| Armenian | 485 | 147 | 0.30 | 1.79x | $0.441 |
| Russian | 471 | 104 | 0.22 | 1.27x | $0.312 |

### Sentence
_One parallel sentence, used to compare Armenian script against Latin transliteration._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 78 | 11 | 0.14 | 1.00x | $0.033 |
| Armenian | 95 | 29 | 0.31 | 2.64x | $0.087 |
| Armenian (Latin) | 94 | 36 | 0.38 | 3.27x | $0.108 |
| Russian | 77 | 18 | 0.23 | 1.64x | $0.054 |
| Spanish | 101 | 18 | 0.18 | 1.64x | $0.054 |
| Turkish | 76 | 20 | 0.26 | 1.82x | $0.060 |
| Georgian | 81 | 25 | 0.31 | 2.27x | $0.075 |

### Greeting
_Everyday short phrase. Short inputs are where per-language overhead hurts most._

| Language | Characters | Tokens | Tokens/char | vs English | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- |
| English | 19 | 6 | 0.32 | 1.00x | $0.018 |
| Armenian | 17 | 11 | 0.65 | 1.83x | $0.033 |
| Armenian (Latin) | 18 | 7 | 0.39 | 1.17x | $0.021 |
| Russian | 17 | 6 | 0.35 | 1.00x | $0.018 |

### Mixed content
_Realistic mixed-content payloads. Each pair is a faithful translation, NOT length-matched, so ratios are indicative rather than precise. Real-world data is rarely pure prose: structured fields, keys and IDs are ASCII and tokenize identically in both languages, so the Armenian penalty applies only to the natural-language fraction._

| Payload | Armenian tokens | English tokens | Multiplier | HY chars |
| --- | --- | --- | --- | --- |
| support ticket | 123 | 111 | 1.11x | 364 |
| log line | 44 | 34 | 1.29x | 116 |
| code switched prose | 60 | 42 | 1.43x | 184 |
| fully armenian prose | 62 | 42 | 1.48x | 181 |

- **support ticket** — Support ticket: English keys and metadata, natural-language fields in each language.
- **log line** — Structured log line: ASCII prefix dominates, only the message is translated.
- **code switched prose** — How Armenian engineers actually write: Armenian grammar, English technical terms. Compare against fully_armenian below.
- **fully armenian prose** — The same content with technical terms translated into Armenian. Isolates the cost of avoiding English loanwords.

