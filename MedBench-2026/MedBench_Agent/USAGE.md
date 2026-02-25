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
- Send them to the POE API (using claude-opus-4.6 by default)
- Save results to `results/MedCOT_results.jsonl`

### 4. Process All Test Files

```bash
# Process all test files
python submit_answers.py --all
```

## Available Test Files

The TEST directory contains 14 benchmark tasks:

1. **MedCOT.jsonl** - Chain of Thought reasoning
2. **MedCallAPI.jsonl** - API calling scenarios
3. **MedCollab.jsonl** - Collaborative tasks
4. **MedDBOps.jsonl** - Database operations
5. **MedDecomp.jsonl** - Problem decomposition
6. **MedDefend.jsonl** - Defense/safety scenarios
7. **MedIntentID.jsonl** - Intent identification
8. **MedLongConv.jsonl** - Long conversations
9. **MedLongQA.jsonl** - Long-form Q&A
10. **MedPathPlan.jsonl** - Clinical pathway planning
11. **MedReflect.jsonl** - Reflective reasoning
12. **MedRetAPI.jsonl** - Retrieval API tasks
13. **MedRoleAdapt.jsonl** - Role adaptation
14. **MedShield.jsonl** - Safety shield tasks

## Command Line Options

### Basic Options

```bash
--api-key YOUR_KEY        # POE API key (or use POE_API_KEY env var)
--model MODEL_NAME        # Model: claude-opus-4.6 (default), gpt-5.1, gemini-3-pro
--test-file FILE          # Process single test file
--test-dir DIR            # Test directory (default: TEST)
--output-dir DIR          # Results directory (default: results)
--all                     # Process all test files
```

### Advanced Options

```bash
--system-prompt "..."     # Add system prompt for context
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
2. **Rate limiting**: Adjust `--delay` if you hit rate limits
3. **Cost control**: Monitor your POE API usage/credits
4. **System prompts**: Customize for each task type for better results
5. **Save progress**: Results are saved incrementally, you can resume if interrupted

## Troubleshooting

### "Error: API key not provided"
- Set the POE_API_KEY environment variable or use --api-key flag

### "Rate limit exceeded"
- Increase --delay value (e.g., --delay 2.0)
- Wait a few minutes and retry

### "Model not found"
- Check model name spelling: claude-opus-4.6, gpt-5.1, or gemini-3-pro
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
