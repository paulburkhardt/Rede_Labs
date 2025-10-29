#!/usr/bin/env python3
"""
Agent Killer Script
Stops the tmux session and cleans up temporary scenario file.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Base paths
SCRIPT_DIR = Path(__file__).parent
TEMP_SCENARIO_PATH = SCRIPT_DIR / "scenario.toml"
TEMP_AGENTS_DIR = SCRIPT_DIR / "temp_agents"
DEFAULT_TMUX_SESSION = "agentbeats-marketplace"


def check_tmux_installed() -> bool:
    """Check if tmux is installed."""
    try:
        subprocess.run(["tmux", "-V"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_tmux_session_exists(session_name: str) -> bool:
    """Check if a tmux session exists."""
    try:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def list_tmux_sessions() -> list:
    """List all tmux sessions."""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')
        return []
    except FileNotFoundError:
        return []


def kill_tmux_session(session_name: str) -> bool:
    """Kill a tmux session."""
    try:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error killing tmux session: {e}")
        return False


def cleanup_temp_files() -> dict:
    """Delete the temporary scenario file and agent cards directory."""
    import shutil
    results = {
        "scenario_deleted": False,
        "agents_dir_deleted": False,
        "errors": []
    }
    
    # Delete temp scenario file
    if TEMP_SCENARIO_PATH.exists():
        try:
            TEMP_SCENARIO_PATH.unlink()
            results["scenario_deleted"] = True
        except Exception as e:
            results["errors"].append(f"Error deleting temp scenario file: {e}")
    
    # Delete temp agents directory
    if TEMP_AGENTS_DIR.exists():
        try:
            shutil.rmtree(TEMP_AGENTS_DIR)
            results["agents_dir_deleted"] = True
        except Exception as e:
            results["errors"].append(f"Error deleting temp agents directory: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Stop AgentBeats agents and clean up temporary files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stop agents with default session name
  uv run tools/kill_agents.py
  
  # Stop agents with custom session name
  uv run tools/kill_agents.py --tmux-session my-session
  
  # List all tmux sessions
  uv run tools/kill_agents.py --list
  
  # Force cleanup even if session doesn't exist
  uv run tools/kill_agents.py --force
        """
    )
    
    parser.add_argument(
        "--tmux-session",
        type=str,
        default=DEFAULT_TMUX_SESSION,
        help=f"Name of the tmux session to kill (default: {DEFAULT_TMUX_SESSION})"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all tmux sessions and exit"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force cleanup even if session doesn't exist"
    )
    
    parser.add_argument(
        "--keep-scenario",
        action="store_true",
        help="Keep the temporary scenario.toml file (don't delete it)"
    )
    
    args = parser.parse_args()
    
    # Check if tmux is installed
    if not check_tmux_installed():
        print("Error: tmux is not installed!")
        print("Please install tmux:")
        print("  macOS: brew install tmux")
        print("  Ubuntu/Debian: sudo apt-get install tmux")
        sys.exit(1)
    
    # List sessions if requested
    if args.list:
        sessions = list_tmux_sessions()
        if sessions:
            print("\nActive tmux sessions:")
            for session in sessions:
                print(f"  - {session}")
            print()
        else:
            print("\nNo active tmux sessions found.\n")
        sys.exit(0)
    
    # Check if session exists
    session_exists = check_tmux_session_exists(args.tmux_session)
    
    if not session_exists and not args.force:
        print(f"\nNo tmux session found with name: {args.tmux_session}")
        
        # Check for other sessions
        sessions = list_tmux_sessions()
        if sessions:
            print("\nActive tmux sessions:")
            for session in sessions:
                print(f"  - {session}")
            print("\nTo kill a specific session, use:")
            print(f"  uv run tools/kill_agents.py --tmux-session SESSION_NAME")
        else:
            print("\nNo active tmux sessions found.")
        
        # Check if temp file exists
        if TEMP_SCENARIO_PATH.exists():
            print(f"\nNote: Temporary scenario file exists: {TEMP_SCENARIO_PATH}")
            print("Use --force to clean it up anyway.")
        
        sys.exit(0)
    
    # Kill the session
    print(f"\n{'='*60}")
    print(f"STOPPING AGENTS")
    print(f"{'='*60}\n")
    
    if session_exists:
        print(f"Killing tmux session: {args.tmux_session}")
        if kill_tmux_session(args.tmux_session):
            print(f"  ✓ Tmux session killed successfully")
        else:
            print(f"  ✗ Failed to kill tmux session")
            if not args.force:
                sys.exit(1)
    else:
        print(f"Tmux session '{args.tmux_session}' not found (--force mode)")
    
    # Clean up temp files
    if not args.keep_scenario:
        print(f"\nCleaning up temporary files...")
        results = cleanup_temp_files()
        
        if results["scenario_deleted"]:
            print(f"  ✓ Deleted: {TEMP_SCENARIO_PATH}")
        elif TEMP_SCENARIO_PATH.exists():
            print(f"  - Temp scenario file exists but wasn't deleted")
        
        if results["agents_dir_deleted"]:
            print(f"  ✓ Deleted: {TEMP_AGENTS_DIR}/")
        elif TEMP_AGENTS_DIR.exists():
            print(f"  - Temp agents directory exists but wasn't deleted")
        
        if not results["scenario_deleted"] and not results["agents_dir_deleted"]:
            print(f"  - No temp files found")
        
        for error in results["errors"]:
            print(f"  ✗ {error}")
    else:
        print(f"\nKeeping temporary files:")
        if TEMP_SCENARIO_PATH.exists():
            print(f"  - {TEMP_SCENARIO_PATH}")
        if TEMP_AGENTS_DIR.exists():
            print(f"  - {TEMP_AGENTS_DIR}/")
    
    print(f"\n{'='*60}")
    print(f"CLEANUP COMPLETE")
    print(f"{'='*60}\n")
    
    print("All agents have been stopped.")
    print("To start agents again, run:")
    print("  uv run tools/start_agents.py --only-white-agents")
    print()


if __name__ == "__main__":
    main()
