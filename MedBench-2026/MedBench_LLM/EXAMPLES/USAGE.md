# MedBench Submission Guide

This guide helps you submit answers to MedBench test questions using your POE API key.

## Quick Start

### 1. Install Dependencies

```bash
pip install openai tqdm
```

### 2. Test Your API Key

```bash
# Set your API key as environment variable
export POE_API_KEY='your-poe-api-key-here'

# Test the connection
python test_api.py
```

Or test with the key directly:
```bash
python test_api.py your-poe-api-key-here
```

### 3. Process a Single Test File

```bash
# Process one test file (e.g., MedCOT - Chain of Thought)
python submit_answers.py --test-file TEST/MedCOT.jsonl --max-questions 5
```

This will:
- Read questions from `TEST/MedCOT.jsonl`
- Send them to the POE API (using claude-sonnet-4.5 by default)
- Save results to `results/MedCOT_results.jsonl`

### 4. Process All Test Files

```bash
# Process all test files
python submit_answers.py --all
```

## Available Test Files

The TEST directory contains 38 benchmark tasks covering diverse medical scenarios:

**Diagnosis & Clinical Reasoning:**
- MedExam, MedDiag, MedMC, DDx-advanced, MedDiffer

**Treatment & Care:**
- MedCare, MedTreat, MedRxPlan, MedRehab, MedPsychCare

**Prescription Review (3 variants):**
- MedRxCheck_SCQ (single-choice), MedRxCheck_MSQ (multiple-choice), MedRxCheck_SQ (subjective Q&A)

**Quality Control:**
- MedChartQC, MedPathQC, MedReportQC

**Medical Documentation:**
- MedRecordGen, MedSummary, SMDoc

**Healthcare Operations:**
- MedInsureCheck, MedInsureCalc, MedHC, MedPHM

**Specialized Domains:**
- MedEthics, MedSafety, MedOutcome, MedExplain, MedAnalysis

**Knowledge & Education:**
- MedLitQA, MedSpeQA, MedPsychQA, MedPopular, MedTeach, MedTerm, MedSynonym

**Primary Care & Others:**
- MedPrimary, MedHG, CMB-Clin-extended

See `README/` directory for detailed descriptions of each task.

## Command Line Options

### Basic Options

```bash
--api-key YOUR_KEY        # POE API key (or use POE_API_KEY env var)
--model MODEL_NAME        # Model: claude-sonnet-4.5 (default), gpt-5.1, gpt-4.1, gemini-3-pro
--test-file FILE          # Process single test file
--test-dir DIR            # Test directory (default: TEST)
--output-dir DIR          # Results directory (default: results)
--all                     # Process all test files
```

### Advanced Options

```bash
--config FILE             # Load settings from config JSON file
--system-prompt "..."     # System prompt override (bypasses config)
--delay SECONDS           # Delay between API calls (default: 1.0)
--max-questions N         # Limit questions per file (for testing)
```

## Usage Examples

### Example 1: Test with a few questions first

```bash
# Process just 3 questions from MedCOT to test
python submit_answers.py \
  --test-file TEST/MedCOT.jsonl \
  --max-questions 3 \
  --delay 2.0
```

### Example 2: Process specific test with custom prompt

```bash
# Process MedCOT with specific system prompt
python submit_answers.py \
  --test-file TEST/MedCOT.jsonl \
  --system-prompt "You are a medical expert. Provide step-by-step diagnostic reasoning."
```

### Example 3: Use different model

```bash
# Use GPT-5.1 instead of Claude
python submit_answers.py \
  --test-file TEST/MedCOT.jsonl \
  --model gpt-5.1
```

### Example 4: Process all tests

```bash
# Process everything (this will take a while!)
python submit_answers.py \
  --all \
  --delay 1.5 \
  --output-dir my_results
```

## Setting Your API Key

### Option 1: Environment Variable (Recommended)

```bash
# Add to your ~/.bashrc or ~/.zshrc
export POE_API_KEY='your-api-key-here'

# Then use scripts without --api-key flag
python submit_answers.py --test-file TEST/MedCOT.jsonl
```

### Option 2: Command Line Argument

```bash
python submit_answers.py \
  --api-key your-api-key-here \
  --test-file TEST/MedCOT.jsonl
```

## Using Configuration Files (Recommended for Production)

Configuration files allow you to set task-specific system prompts and default settings.

### 1. Create Your Config File

Copy the example config:
```bash
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "api_key": "your-poe-api-key-here",
  "model": "claude-sonnet-4.5",
  "output_dir": "results",
  "delay": 1.0,
  "system_prompts": {
    "MedExam": "You are a medical expert taking examinations...",
    "MedRxCheck_SCQ": "You are a clinical pharmacist. Answer single-choice...",
    "MedRxCheck_MSQ": "You are a clinical pharmacist. Answer multiple-choice...",
    "MedRxCheck_SQ": "You are a clinical pharmacist conducting prescription review...",
    "default": "You are a medical expert..."
  }
}
```

### 2. Run with Config File

```bash
# Process single file using config
python submit_answers.py --config config.json --test-file TEST/MedExam.jsonl

# Process all files using config
python submit_answers.py --config config.json --all
```

### 3. Smart Prompt Matching

The system uses **smart matching** for system prompts:

1. **Exact match**: `MedRxCheck_MSQ` → uses `MedRxCheck_MSQ` prompt
2. **Base match**: `MedRxCheck_MSQ` → falls back to `MedRxCheck` if exact not found
3. **Default**: Uses `default` prompt if no match found

**Example:** For `MedRxCheck_MSQ.jsonl`:
- Tries `MedRxCheck_MSQ` prompt first (specific for multiple-choice)
- Falls back to `MedRxCheck` prompt (general prescription review)
- Falls back to `default` prompt (general medical expert)

This allows you to:
- Set specific prompts for variants (e.g., `MedRxCheck_MSQ`, `MedRxCheck_SCQ`)
- Set a base prompt for all variants (e.g., `MedRxCheck`)
- Have a default for all other tasks

### 4. Config Priority

Settings are applied in this order (higher priority first):
1. Command-line arguments
2. Config file
3. Default values

**Example:**
```bash
# Uses gpt-5.1 despite config saying claude-sonnet-4.5
python submit_answers.py --config config.json --model gpt-5.1 --all
```

## Output Format

Results are saved as JSONL files in the `results/` directory:

```json
{"question": "患者信息...", "answer": "模型回答...", "other": {"id": 97, "source": "MedCOT_V4"}}
```

Each line contains:
- `question`: Original test question
- `answer`: Model's response (filled by the script)
- `other`: Metadata (id, source)

## Tips

1. **Start small**: Use `--max-questions 5` to test first
2. **Use config files**: Set up task-specific prompts in `config.json` for better results
3. **Rate limiting**: Adjust `--delay` if you hit rate limits
4. **Cost control**: Monitor your POE API usage/credits
5. **System prompts**: The config file includes optimized prompts for all 38 tasks
6. **Variant tasks**: MedRxCheck has 3 variants (SCQ/MSQ/SQ) with specific prompts for each
7. **Save progress**: Results are saved incrementally, you can resume if interrupted

## Troubleshooting

### "Error: API key not provided"
- Set the POE_API_KEY environment variable or use --api-key flag

### "Rate limit exceeded"
- Increase --delay value (e.g., --delay 2.0)
- Wait a few minutes and retry

### "Model not found"
- Check model name spelling: claude-sonnet-4.5, gpt-5.1, or gemini-3-pro
- Verify your POE account has access to the model

### Script stops midway
- Results are saved as they're generated
- Restart with the same command, or process remaining files individually

## Next Steps

After generating results:
1. Review your results in the `results/` directory
2. Check answer quality and format
3. Submit to MedBench evaluation system (follow official submission guidelines)
4. Check the leaderboard for your scores

## File Structure

```
MedBench_Agent/
├── TEST/                    # Test questions (input)
│   ├── MedCOT.jsonl
│   ├── MedDecomp.jsonl
│   └── ...
├── results/                 # Generated answers (output)
│   ├── MedCOT_results.jsonl
│   ├── MedDecomp_results.jsonl
│   └── ...
├── submit_answers.py        # Main submission script
├── test_api.py             # API connection test
├── config.example.json     # Configuration example
└── USAGE.md                # This file
```

## Support

For MedBench-specific questions, refer to the README files in the `README/` directory for each task.
