#!/usr/bin/env python3
"""
Test script to verify max_tokens behavior with excessive values
"""
from dotenv import load_dotenv
load_dotenv()  # Load .env file

from pdf_to_md_llm.converter import convert_pdf_to_markdown

# Test with excessive max_tokens (way beyond the 8,192 limit for Haiku)
print("=" * 60)
print("Testing with max_tokens = 10000 (exceeds 8192 model limit)")
print("=" * 60)

try:
    result = convert_pdf_to_markdown(
        pdf_path="input/basic-text.pdf",
        output_path="test_output_10k.md",
        max_tokens=10000,  # Exceeds the 8,192 limit
        verbose=True
    )
    print("\nConversion completed successfully!")
    print("This means the API either:")
    print("  - Silently capped max_tokens to the model limit")
    print("  - Or truncated the output without error")

except Exception as e:
    print(f"\nError occurred: {type(e).__name__}")
    print(f"   Message: {e}")
    print("\nThis is the expected behavior - should fail with token limit error")
