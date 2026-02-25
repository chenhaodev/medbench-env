#!/usr/bin/env python3
"""
MedBench Answer Submission Script

This script processes test questions from MedBench dataset and generates answers
using POE API with your chosen model.
"""

import openai
import json
import os
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import time
from tqdm import tqdm


MAX_RETRIES = 3
RETRY_BACKOFF = [5, 15, 30]  # seconds between retries


class MedBenchSubmitter:
    """Handler for submitting answers to MedBench test questions"""

    def __init__(self, api_key: str, model: str = "claude-opus-4.6",
                 output_dir: str = "results"):
        """
        Initialize the submitter

        Args:
            api_key: Your POE API key
            model: Model to use (claude-opus-4.6, claude-sonnet-4.5, gpt-5.1, gpt-4.1, gemini-3-pro)
            output_dir: Directory to save results
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1",
        )
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def load_test_file(self, filepath: str) -> List[Dict]:
        """Load test questions from JSONL file"""
        questions = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
        return questions

    def load_existing_results(self, output_file: Path) -> Dict[int, Dict]:
        """
        Load existing results keyed by question id, skipping error entries.
        Returns dict mapping question id -> result dict.
        """
        if not output_file.exists():
            return {}
        existing = {}
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    answer = item.get('answer', '')
                    qid = item.get('other', {}).get('id')
                    # Keep only valid (non-error) answers
                    if answer and 'ERROR' not in answer and 'Connection error' not in answer:
                        existing[qid] = item
                except json.JSONDecodeError:
                    pass
        return existing

    def query_model(self, question: str, system_prompt: Optional[str] = None) -> str:
        """
        Query the model with a question, retrying on connection errors.

        Args:
            question: The question to ask
            system_prompt: Optional system prompt for context

        Returns:
            Model's response, or error string after all retries exhausted
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                chat = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                return chat.choices[0].message.content
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF[attempt]
                    print(f"\nError (attempt {attempt + 1}/{MAX_RETRIES}): {e} — retrying in {wait}s")
                    time.sleep(wait)
                else:
                    print(f"\nError querying model after {MAX_RETRIES} attempts: {e}")
        return f"ERROR: {str(last_error)}"

    def process_test_file(self, test_file: str, system_prompt: Optional[str] = None,
                          delay: float = 1.0, max_questions: Optional[int] = None) -> str:
        """
        Process all questions in a test file, resuming from existing valid results.

        Args:
            test_file: Path to test JSONL file
            system_prompt: Optional system prompt
            delay: Delay between API calls (seconds)
            max_questions: Maximum number of questions to process (None = all)

        Returns:
            Path to output file
        """
        test_path = Path(test_file)
        test_name = test_path.stem
        output_file = self.output_dir / f"{test_name}_results.jsonl"

        print(f"\n{'='*60}")
        print(f"Processing: {test_name}")
        print(f"Model: {self.model}")
        print(f"{'='*60}\n")

        # Load questions
        questions = self.load_test_file(test_file)
        if max_questions:
            questions = questions[:max_questions]

        # Load existing valid results for resume support
        existing = self.load_existing_results(output_file)
        skip_count = sum(
            1 for q in questions
            if q.get('other', {}).get('id') in existing
        )
        if skip_count:
            print(f"Resuming: {skip_count}/{len(questions)} already answered, skipping those")

        print(f"Loaded {len(questions)} questions ({len(questions) - skip_count} to process)")

        # Process each question
        results = []
        to_process = 0
        for i, item in enumerate(tqdm(questions, desc="Processing questions")):
            qid = item.get('other', {}).get('id')

            # Skip already-answered questions
            if qid in existing:
                results.append(existing[qid])
                continue

            to_process += 1
            answer = self.query_model(item['question'], system_prompt)

            result = {
                'question': item['question'],
                'answer': answer,
                'other': item.get('other', {})
            }
            results.append(result)

            # Delay to avoid rate limiting (only between actual API calls)
            if to_process > 0 and i < len(questions) - 1:
                time.sleep(delay)

        # Save results preserving original question order
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"\n✓ Results saved to: {output_file}")
        return str(output_file)

    def process_all_tests(self, test_dir: str = "TEST",
                          system_prompt: Optional[str] = None,
                          delay: float = 1.0,
                          max_questions: Optional[int] = None):
        """
        Process all test files in the TEST directory.
        """
        test_path = Path(test_dir)
        test_files = sorted(test_path.glob("*.jsonl"))

        print(f"\nFound {len(test_files)} test files")

        for test_file in test_files:
            self.process_test_file(
                str(test_file),
                system_prompt=system_prompt,
                delay=delay,
                max_questions=max_questions
            )

        print(f"\n{'='*60}")
        print("All tests completed!")
        print(f"Results saved in: {self.output_dir}")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Submit answers to MedBench test questions using POE API"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="POE API key (or set POE_API_KEY environment variable)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="claude-opus-4.6",
        choices=["claude-opus-4.6", "claude-sonnet-4.5", "gpt-5.1", "gpt-4.1", "gemini-3-pro"],
        help="Model to use for answers (default: claude-opus-4.6)"
    )

    parser.add_argument(
        "--test-file",
        type=str,
        help="Single test file to process (e.g., TEST/MedCOT.jsonl)"
    )

    parser.add_argument(
        "--test-dir",
        type=str,
        default="TEST",
        help="Directory containing test files (default: TEST)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Directory to save results (default: results)"
    )

    parser.add_argument(
        "--system-prompt",
        type=str,
        help="Optional system prompt to provide context"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)"
    )

    parser.add_argument(
        "--max-questions",
        type=int,
        help="Maximum number of questions to process per file (for testing)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all test files in TEST directory"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("POE_API_KEY")
    if not api_key:
        print("Error: API key not provided!")
        print("Use --api-key argument or set POE_API_KEY environment variable")
        return

    # Initialize submitter
    submitter = MedBenchSubmitter(
        api_key=api_key,
        model=args.model,
        output_dir=args.output_dir
    )

    # Process files
    if args.all:
        submitter.process_all_tests(
            test_dir=args.test_dir,
            system_prompt=args.system_prompt,
            delay=args.delay,
            max_questions=args.max_questions
        )
    elif args.test_file:
        submitter.process_test_file(
            args.test_file,
            system_prompt=args.system_prompt,
            delay=args.delay,
            max_questions=args.max_questions
        )
    else:
        print("Error: Must specify --test-file or --all")
        parser.print_help()


if __name__ == "__main__":
    main()
