import subprocess
import sys
import os

def run_map_creator():
    print("Starting MapCreator...")
    try:
        # Execute MapCreator.py script
        subprocess.run([sys.executable, 'MapCreator.py'], check=True)
    except subprocess.CalledProcessError as e:
        print("MapCreator failed. Exiting...")
        sys.exit(e.returncode)
    print("MapCreator completed.")

def run_main():
    print("Starting Main...")
    try:
        # Execute Main.py script
        subprocess.run([sys.executable, 'Main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print("Main failed. Exiting...")
        sys.exit(e.returncode)
    print("Main completed.")

def run_graph_generator():
    print("Starting GraphGenerator...")
    try:
        # Use Popen instead of run to avoid blocking the terminal
        subprocess.Popen([sys.executable, 'GraphGenerator.py'])
    except Exception as e:
        print("GraphGenerator failed. Exiting...")
        sys.exit(1)
    print("GraphGenerator started in a separate process.")

if __name__ == '__main__':
    # Run MapCreator
    run_map_creator()

    # Wait for user input before running Main
    input("Press enter to start the Main program...")

    # Run Main
    run_main()

    input("Press enter to start the Graph Generator...")

    # Run GraphGenerator
    run_graph_generator()
