#!/usr/bin/env python3
"""
Minimal Discord bot launcher with error handling.
"""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, 'discord_bot.py'],
    capture_output=True,
    text=True,
    timeout=30
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nExit Code: {result.returncode}")
