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
from typing import List, Dict
import time
from tqdm import tqdm


class MedBenchSubmitter:
    """Handler for submitting answers to MedBench test questions"""

    def __init__(self, api_key: str, model: str = "gpt-4.1",
                 output_dir: str = "results", system_prompts: Dict[str, str] = None):
        """
        Initialize the submitter

        Args:
            api_key: Your POE API key
            model: Model to use (claude-sonnet-4.5, gpt-5.1, gpt-4.1, gemini-3-pro)
            output_dir: Directory to save results
            system_prompts: Dict mapping task names to system prompts
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1",
        )
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.system_prompts = system_prompts or {}

    def get_system_prompt(self, test_name: str) -> str:
        """
        Get system prompt for a test with smart matching

        Tries in order:
        1. Exact match (e.g., "MedRxCheck_MSQ")
        2. Base name match (e.g., "MedRxCheck" for "MedRxCheck_MSQ")
        3. Default prompt

        Args:
            test_name: Name of the test file (without extension)

        Returns:
            System prompt string
        """
        if not self.system_prompts:
            return None

        # Try exact match first
        if test_name in self.system_prompts:
            return self.system_prompts[test_name]

        # Try base name (remove suffix after underscore)
        if '_' in test_name:
            base_name = test_name.rsplit('_', 1)[0]
            if base_name in self.system_prompts:
                return self.system_prompts[base_name]

        # Fall back to default
        return self.system_prompts.get('default', None)

    def load_test_file(self, filepath: str) -> List[Dict]:
        """Load test questions from JSONL file"""
        questions = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
        return questions

    def query_model(self, question: str, system_prompt: str = None) -> str:
        """
        Query the model with a question

        Args:
            question: The question to ask
            system_prompt: Optional system prompt for context

        Returns:
            Model's response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})

        try:
            chat = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"\nError querying model: {e}")
            return f"ERROR: {str(e)}"

    def process_test_file(self, test_file: str, system_prompt_override: str = None,
                         delay: float = 1.0, max_questions: int = None) -> str:
        """
        Process all questions in a test file

        Args:
            test_file: Path to test JSONL file
            system_prompt_override: Optional system prompt override (bypasses config)
            delay: Delay between API calls (seconds)
            max_questions: Maximum number of questions to process (None = all)

        Returns:
            Path to output file
        """
        test_path = Path(test_file)
        test_name = test_path.stem

        # Get system prompt with smart matching
        system_prompt = system_prompt_override or self.get_system_prompt(test_name)

        print(f"\n{'='*60}")
        print(f"Processing: {test_name}")
        print(f"Model: {self.model}")
        if system_prompt:
            print(f"System prompt: {system_prompt[:80]}..." if len(system_prompt) > 80 else f"System prompt: {system_prompt}")
        print(f"{'='*60}\n")

        # Load questions
        questions = self.load_test_file(test_file)
        if max_questions:
            questions = questions[:max_questions]

        print(f"Loaded {len(questions)} questions")

        # Process each question
        results = []
        for i, item in enumerate(tqdm(questions, desc="Processing questions")):
            question = item['question']

            # Query model
            answer = self.query_model(question, system_prompt)

            # Save result
            result = {
                'question': question,
                'answer': answer,
                'other': item.get('other', {})
            }
            results.append(result)

            # Delay to avoid rate limiting
            if i < len(questions) - 1:
                time.sleep(delay)

        # Save results
        output_file = self.output_dir / f"{test_name}_results.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"\n✓ Results saved to: {output_file}")
        return str(output_file)

    def process_all_tests(self, test_dir: str = "TEST",
                         system_prompt_override: str = None,
                         delay: float = 1.0,
                         max_questions: int = None):
        """
        Process all test files in the TEST directory

        Args:
            test_dir: Directory containing test files
            system_prompt_override: Optional system prompt override (bypasses config)
            delay: Delay between API calls (seconds)
            max_questions: Maximum questions per file (None = all)
        """
        test_path = Path(test_dir)
        test_files = sorted(test_path.glob("*.jsonl"))

        print(f"\nFound {len(test_files)} test files")

        for test_file in test_files:
            self.process_test_file(
                str(test_file),
                system_prompt_override=system_prompt_override,
                delay=delay,
                max_questions=max_questions
            )

        print(f"\n{'='*60}")
        print("All tests completed!")
        print(f"Results saved in: {self.output_dir}")
        print(f"{'='*60}")


def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file"""
    if not os.path.exists(config_file):
        return {}
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Submit answers to MedBench test questions using POE API"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to config JSON file (optional)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="POE API key (or set POE_API_KEY environment variable)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1",
        choices=["claude-sonnet-4.5", "gpt-5.1", "gpt-4.1", "gemini-3-pro"],
        help="Model to use for answers (default: gpt-4.1)"
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
        help="Optional system prompt override (bypasses config file)"
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

    # Load config file if provided
    config = {}
    if args.config:
        config = load_config(args.config)
        print(f"Loaded config from: {args.config}")

    # Get API key (command line > config file > environment variable)
    api_key = args.api_key or config.get("api_key") or os.getenv("POE_API_KEY")
    if not api_key:
        print("Error: API key not provided!")
        print("Use --api-key argument, config file, or set POE_API_KEY environment variable")
        return

    # Get model (command line > config file > default)
    model = args.model if args.model != "gpt-4.1" else config.get("model", "gpt-4.1")

    # Get output dir (command line > config file > default)
    output_dir = args.output_dir if args.output_dir != "results" else config.get("output_dir", "results")

    # Get delay (command line > config file > default)
    delay = args.delay if args.delay != 1.0 else config.get("delay", 1.0)

    # Get system prompts from config
    system_prompts = config.get("system_prompts", {})

    # Initialize submitter
    submitter = MedBenchSubmitter(
        api_key=api_key,
        model=model,
        output_dir=output_dir,
        system_prompts=system_prompts
    )

    # Process files
    if args.all:
        submitter.process_all_tests(
            test_dir=args.test_dir,
            system_prompt_override=args.system_prompt,
            delay=delay,
            max_questions=args.max_questions
        )
    elif args.test_file:
        submitter.process_test_file(
            args.test_file,
            system_prompt_override=args.system_prompt,
            delay=delay,
            max_questions=args.max_questions
        )
    else:
        print("Error: Must specify --test-file or --all")
        parser.print_help()


if __name__ == "__main__":
    main()
