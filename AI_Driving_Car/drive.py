import subprocess
import sys
import os


def run_map_creator():
    print("Starting MapCreator...")
    try:
        subprocess.run([sys.executable, 'MapCreator.py'], check=True)
    except subprocess.CalledProcessError as e:
        print("MapCreator failed. Exiting...")
        sys.exit(e.returncode)
    print("MapCreator completed.")


def run_main():
    print("Starting Main...")
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print("Main failed. Exiting...")
        sys.exit(e.returncode)
    print("Main completed.")


if __name__ == '__main__':
    # Esegui il MapCreator
    run_map_creator()

    # Attendi l'input dell'utente prima di eseguire il Main
    input("Press enter to start the Main program...")

    # Esegui il Main
    run_main()
