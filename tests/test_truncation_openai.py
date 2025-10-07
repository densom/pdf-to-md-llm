#!/usr/bin/env python3
"""
Test script to verify that TruncationError is raised for OpenAI when responses are truncated
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file

import os
from pdf_to_md_llm.converter import convert_pdf_to_markdown
from pdf_to_md_llm.providers import TruncationError

# Check if OpenAI API key is available
if not os.environ.get("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not found - skipping OpenAI test")
    exit(0)

print("=" * 60)
print("Testing TruncationError (OpenAI) with max_tokens = 100")
print("=" * 60)

try:
    result = convert_pdf_to_markdown(
        pdf_path="input/basic-text.pdf",
        output_path="test_output_truncation_openai.md",
        provider="openai",
        max_tokens=100,  # Very small - will definitely truncate
        verbose=True
    )
    print("\n[FAIL] Conversion completed without error!")
    print("This should NOT happen - truncation should raise TruncationError")

except TruncationError as e:
    print(f"\n[SUCCESS] TruncationError raised as expected!")
    print(f"   Message: {e}")
    print("\nThis is the correct behavior - truncation is now detected!")

except Exception as e:
    print(f"\n[FAIL] Wrong exception type: {type(e).__name__}")
    print(f"   Message: {e}")
    print("\nExpected TruncationError, got something else")
