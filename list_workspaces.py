"""
Script to list available Roboflow workspaces for your API key.
"""

import sys
from roboflow import Roboflow

def main():
    """List available workspaces."""
    print("=" * 60)
    print("Roboflow Workspace Lister")
    print("=" * 60)
    print()
    
    api_key = input("Enter your Roboflow API Key: ").strip()
    if not api_key:
        print("Error: API key is required.")
        sys.exit(1)
    
    try:
        print("Connecting to Roboflow...")
        rf = Roboflow(api_key=api_key)
        
        # Try to get user info or list workspaces
        # The Roboflow Python SDK might have different methods
        try:
            # Try accessing the account/workspace info
            print("\nAttempting to list workspaces...")
            
            # Alternative: Try to access a known endpoint
            # We can try to get the account info
            account = rf.account()
            print(f"Account info: {account}")
            
        except Exception as e:
            print(f"\nNote: Direct workspace listing not available: {str(e)}")
            print("\nTo find your workspace name:")
            print("1. Go to https://app.roboflow.com")
            print("2. Check the URL - it will show your workspace name")
            print("3. Or check the workspace name in the top-left corner")
            print("\nCommon workspace name formats:")
            print("- Your username (e.g., 'acarem16')")
            print("- Organization name")
            print("- Custom workspace name")
            
            # Try to help by suggesting common patterns
            print("\nPlease check your Roboflow dashboard for the correct workspace name.")
            
    except Exception as e:
        print(f"Error connecting to Roboflow: {str(e)}")
        print("\nPlease verify:")
        print("1. Your API key is correct")
        print("2. You have internet connection")
        print("3. Your Roboflow account is active")

if __name__ == "__main__":
    main()

