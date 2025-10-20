#!/usr/bin/env python3
"""
Automated test runner for Pitstop F1 MCP Server tools.

Runs all tool test suites and reports results.
"""

import sys
import json
import time
import traceback
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class ToolTester:
    """Test runner for MCP tools."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }

    def test_tool_module(self, tool_path: Path) -> Dict[str, Any]:
        """Test a single tool module."""
        test_result = {
            "tool": tool_path.stem,
            "path": str(tool_path),
            "status": "unknown",
            "duration": 0.0,
            "error": None
        }

        start_time = time.time()

        try:
            # Skip __init__.py files
            if tool_path.stem == "__init__":
                test_result["status"] = "skipped"
                test_result["error"] = "Init file"
                return test_result

            # Execute the module (runs if __name__ == "__main__" block)
            print(f"\n{'='*60}")
            print(f"Testing: {tool_path.stem}")
            print(f"{'='*60}")

            with open(tool_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Check if module has test block
            if 'if __name__ == "__main__"' not in code:
                test_result["status"] = "skipped"
                test_result["error"] = "No test block found"
                return test_result

            # Execute the module
            exec(compile(code, str(tool_path), 'exec'), {'__name__': '__main__'})

            test_result["status"] = "passed"
            print(f"[PASS] {tool_path.stem}")

        except KeyboardInterrupt:
            raise
        except Exception as e:
            test_result["status"] = "failed"
            test_result["error"] = f"{type(e).__name__}: {str(e)}"
            print(f"[FAIL] {tool_path.stem}")
            print(f"  Error: {test_result['error']}")
            traceback.print_exc()

        finally:
            test_result["duration"] = time.time() - start_time

        return test_result

    def discover_tools(self) -> List[Path]:
        """Discover all tool Python files."""
        tools_dir = Path("tools")

        if not tools_dir.exists():
            print("Error: tools/ directory not found")
            return []

        # Find all .py files in tools directory
        tool_files = list(tools_dir.rglob("*.py"))

        # Sort for consistent execution order
        tool_files.sort()

        print(f"\nDiscovered {len(tool_files)} tool files")
        return tool_files

    def run_all_tests(self) -> bool:
        """Run all tool tests."""
        print("\n" + "="*70)
        print("PITSTOP F1 MCP SERVER - TOOL TEST SUITE")
        print("="*70)

        tool_files = self.discover_tools()

        if not tool_files:
            print("No tool files found!")
            return False

        print(f"\nRunning tests for {len(tool_files)} tools...\n")

        for tool_path in tool_files:
            result = self.test_tool_module(tool_path)
            self.results["tests"].append(result)

            # Update summary
            self.results["summary"]["total"] += 1
            if result["status"] == "passed":
                self.results["summary"]["passed"] += 1
            elif result["status"] == "failed":
                self.results["summary"]["failed"] += 1
            elif result["status"] == "skipped":
                self.results["summary"]["skipped"] += 1

        return self.print_summary()

    def print_summary(self) -> bool:
        """Print test summary and return success status."""
        summary = self.results["summary"]

        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total:   {summary['total']}")
        print(f"Passed:  {summary['passed']} [PASS]")
        print(f"Failed:  {summary['failed']} [FAIL]")
        print(f"Skipped: {summary['skipped']} [SKIP]")
        print("="*70)

        # List failed tests
        if summary['failed'] > 0:
            print("\nFailed Tests:")
            for test in self.results["tests"]:
                if test["status"] == "failed":
                    print(f"  [FAIL] {test['tool']}: {test['error']}")

        # Save results to JSON
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to: test_results.json")

        # Return success if no failures
        return summary['failed'] == 0


def main():
    """Main test runner entry point."""
    try:
        tester = ToolTester()
        success = tester.run_all_tests()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nFatal error in test runner: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
