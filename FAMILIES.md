## Armenian across tokenizer families

**Spread:** the same Armenian text costs 873 tokens in GPT-4 / GPT-3.5 and 147 in GPT-4o and newer -- 5.9x apart, for identical input.

### Paragraph
_Same meaning, same approximate length (~470-485 characters) in every language._

| Family | Vocab | Armenian tokens | English tokens | Multiplier | Tokens/char | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 873 | 82 | 10.65x | 1.80 | $2.619 |
| GPT-4o and newer | 200,019 | 147 | 82 | 1.79x | 0.30 | $0.441 |
| Llama 3.1 | 128,256 | 786 | 82 | 9.59x | 1.62 | $2.358 |
| Mistral v0.3 | 32,768 | 534 | 85 | 6.28x | 1.10 | $1.602 |
| Gemma 2 | 256,000 | 273 | 83 | 3.29x | 0.56 | $0.819 |
| Qwen 2.5 | 151,665 | 476 | 82 | 5.80x | 0.98 | $1.428 |
| DeepSeek-V3 | 128,815 | 273 | 82 | 3.33x | 0.56 | $0.819 |

### Sentence
_One parallel sentence, used to compare Armenian script against Latin transliteration._

| Family | Vocab | Armenian tokens | English tokens | Multiplier | Tokens/char | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 178 | 12 | 14.83x | 1.87 | $0.534 |
| GPT-4o and newer | 200,019 | 29 | 11 | 2.64x | 0.31 | $0.087 |
| Llama 3.1 | 128,256 | 155 | 12 | 12.92x | 1.63 | $0.465 |
| Mistral v0.3 | 32,768 | 108 | 12 | 9.00x | 1.14 | $0.324 |
| Gemma 2 | 256,000 | 47 | 11 | 4.27x | 0.49 | $0.141 |
| Qwen 2.5 | 151,665 | 95 | 12 | 7.92x | 1.00 | $0.285 |
| DeepSeek-V3 | 128,815 | 47 | 11 | 4.27x | 0.49 | $0.141 |

### Greeting
_Everyday short phrase. Short inputs are where per-language overhead hurts most._

| Family | Vocab | Armenian tokens | English tokens | Multiplier | Tokens/char | Cost / 1k calls |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 31 | 6 | 5.17x | 1.82 | $0.093 |
| GPT-4o and newer | 200,019 | 11 | 6 | 1.83x | 0.65 | $0.033 |
| Llama 3.1 | 128,256 | 30 | 6 | 5.00x | 1.76 | $0.090 |
| Mistral v0.3 | 32,768 | 23 | 6 | 3.83x | 1.35 | $0.069 |
| Gemma 2 | 256,000 | 14 | 6 | 2.33x | 0.82 | $0.042 |
| Qwen 2.5 | 151,665 | 17 | 6 | 2.83x | 1.00 | $0.051 |
| DeepSeek-V3 | 128,815 | 16 | 6 | 2.67x | 0.94 | $0.048 |

### Why: Armenian coverage in the vocabulary

| Family | Vocab | Armenian tokens | Multi-char | Longest Armenian token | Paragraph cost |
| --- | --- | --- | --- | --- | --- |
| GPT-4 / GPT-3.5 | 100,277 | 0 | 0 | none | 873 tokens |
| Llama 3.1 | 128,256 | 1 | 0 | `ա` | 786 tokens |
| Mistral v0.3 | 32,768 | 28 | 0 | `ս` | 534 tokens |
| Qwen 2.5 | 151,665 | 72 | 0 | `ց` | 476 tokens |
| Gemma 2 | 256,000 | 231 | 118 | `ագրություններ` | 273 tokens |
| DeepSeek-V3 | 128,815 | 189 | 118 | `ությունը` | 273 tokens |
| GPT-4o and newer | 200,019 | 1,726 | 1,578 | `հնարավորություն` | 147 tokens |

### What each row is

- **GPT-4 / GPT-3.5** — `cl100k_base` -- OpenAI's previous generation
- **GPT-4o and newer** — `o200k_base` -- OpenAI's current generation
- **Llama 3.1** — `NousResearch/Meta-Llama-3.1-8B` -- ungated mirror of meta-llama/Llama-3.1-8B
- **Mistral v0.3** — `mistralai/Mistral-7B-Instruct-v0.3` -- also backs Mixtral
- **Gemma 2** — `unsloth/gemma-2-9b` -- ungated mirror; the closest public relative of Gemini's tokenizer, not Gemini itself
- **Qwen 2.5** — `Qwen/Qwen2.5-7B` -- Alibaba; also backs many fine-tunes
- **DeepSeek-V3** — `deepseek-ai/DeepSeek-V3` -- DeepSeek's current tokenizer

### Not measured

- **Claude** — Anthropic does not publish a tokenizer for Claude 3 and later. Token counts are available only through the API's count_tokens endpoint.
- **Gemini** — Google does not publish Gemini's tokenizer. The Gemma 2 row above is a relative of it, not a substitute -- treat it as an indication, not a measurement.

