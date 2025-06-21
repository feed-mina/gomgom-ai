#!/usr/bin/env python3
"""
Database Setup Script for GomGom AI FastAPI Project

This script provides an interactive way to set up the database with or without spatial extensions.
"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.init_db import init_database

def main():
    print("=" * 60)
    print("GomGom AI Database Setup")
    print("=" * 60)
    print()
    print("Choose your database setup option:")
    print()
    print("1. Standard Setup (Recommended)")
    print("   - Basic indexes for performance")
    print("   - Simple latitude/longitude indexing")
    print("   - No additional PostgreSQL extensions required")
    print()
    print("2. Spatial Setup (Advanced)")
    print("   - Advanced spatial indexes with earthdistance extension")
    print("   - Enables distance calculations and spatial queries")
    print("   - Requires earthdistance and cube extensions")
    print()
    print("3. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\nStarting standard database setup...")
                init_database(use_spatial=False)
                break
            elif choice == "2":
                print("\nStarting spatial database setup...")
                print("Note: This requires the earthdistance extension to be available in PostgreSQL.")
                confirm = input("Continue with spatial setup? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    init_database(use_spatial=True)
                else:
                    print("Spatial setup cancelled.")
                break
            elif choice == "3":
                print("Setup cancelled.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\nSetup cancelled by user.")
            break
        except Exception as e:
            print(f"\nError during setup: {e}")
            print("Please check your PostgreSQL configuration and try again.")
            break

if __name__ == "__main__":
    main() 