#!/usr/bin/env python3
"""
A script that takes multiple parameters and prints them to the terminal.
Supports both positional arguments and named arguments (flags).

Usage examples:
    python print_params.py arg1 arg2 arg3
    python print_params.py --name John --age 25 --city "New York"
    python print_params.py arg1 arg2 --verbose --output file.txt
"""

import argparse
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Print multiple parameters to terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python print_params.py hello world
  python print_params.py --name John --age 25
  python print_params.py item1 item2 --verbose --output results.txt
        """
    )
    
    # Add common named arguments
    parser.add_argument("--name", type=str, help="Name parameter")
    parser.add_argument("--age", type=int, help="Age parameter")
    parser.add_argument("--city", type=str, help="City parameter")
    parser.add_argument("--output", type=str, help="Output file parameter")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Add positional arguments (variable number)
    parser.add_argument("items", nargs="*", help="Positional arguments")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print header
    print("=" * 50)
    print("PARAMETER PRINTER SCRIPT")
    print("=" * 50)
    print(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Print positional arguments
    if args.items:
        print("POSITIONAL ARGUMENTS:")
        for i, item in enumerate(args.items, 1):
            print(f"  {i}. {item}")
        print()
    
    # Print named arguments
    named_args = []
    if args.name:
        named_args.append(("name", args.name))
    if args.age:
        named_args.append(("age", args.age))
    if args.city:
        named_args.append(("city", args.city))
    if args.output:
        named_args.append(("output", args.output))
    
    if named_args:
        print("NAMED ARGUMENTS:")
        for key, value in named_args:
            print(f"  --{key}: {value}")
        print()
    
    # Print flags
    flags = []
    if args.verbose:
        flags.append("verbose")
    if args.debug:
        flags.append("debug")
    
    if flags:
        print("FLAGS:")
        for flag in flags:
            print(f"  --{flag}: enabled")
        print()
    
    # Summary
    total_params = len(args.items) + len(named_args) + len(flags)
    print("SUMMARY:")
    print(f"  Total positional arguments: {len(args.items)}")
    print(f"  Total named arguments: {len(named_args)}")
    print(f"  Total flags: {len(flags)}")
    print(f"  Total parameters: {total_params}")
    
    # Verbose output
    if args.verbose:
        print("\nVERBOSE OUTPUT:")
        print(f"  Script name: {sys.argv[0]}")
        print(f"  Python version: {sys.version.split()[0]}")
        print(f"  Command line: {' '.join(sys.argv)}")
    
    # Debug output
    if args.debug:
        print("\nDEBUG OUTPUT:")
        print(f"  Raw args object: {args}")
        print(f"  sys.argv: {sys.argv}")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
