# src/setup_dirs.py
import os

def create_directories():
    # Get the current directory (where the script is running)
    current_dir = os.getcwd()
    
    # Create paths
    checkpoints_dir = os.path.join(current_dir, 'checkpoints')
    party_votes_dir = os.path.join(checkpoints_dir, 'party_votes')
    time_trends_dir = os.path.join(checkpoints_dir, 'time_trends')
    
    # Create directories
    os.makedirs(party_votes_dir, exist_ok=True)
    os.makedirs(time_trends_dir, exist_ok=True)
    
    print(f"Created directories:")
    print(f"- {checkpoints_dir}")
    print(f"- {party_votes_dir}")
    print(f"- {time_trends_dir}")

if __name__ == "__main__":
    create_directories()