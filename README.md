# Racing Simulation with NEAT

This project is a racing simulation using Pygame and the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. The simulation involves cars that evolve over time to improve their performance on a custom-created track.

## Requirements

Ensure you have all the necessary libraries installed, in particular:

- `pygame`
- `pygame_gui`
- `matplotlib`
- `pandas`
- `neat-python`

You can install these libraries using pip:

```bash
pip install pygame pygame_gui matplotlib pandas neat-python==0.92
```

## Project Structure

The project consists of the following scripts:

1. MapCreator.py: Allows the user to create a custom track by drawing paths.
2. main.py: Runs the racing simulation using NEAT.
3. GraphGenerator.py: Generates graphs to visualize the performance of the cars over generations.
4. drive.py: Controls the execution flow of the project, running the map creator, main simulation, and graph generator sequentially.

## How to Run

To run the project, use the following command from your terminal:

```bash
python3 drive.py
```

## Steps

### Run the Map Creator

This step launches the MapCreator tool to create a custom track.
- Draw the track using your mouse. You can clear the track, adjust the brush width, and hide/show the UI using the provided buttons.
- Move the white line on the track, as the cars will spawn on it. Use the following keys to control the white line:
  - Arrow Keys: Move the white line.
  - R: Rotate the white line.
  - Enter: Save the track as track.png.
  - Esc: Show the UI if it is hidden.
- Recommendation: Hide the UI by pressing the toggle button before pressing Enter to save the track.
- If you want to use a track that is already drawn, you can simply close the MapCreator.

### Run the Main Simulation

- After creating and saving the track, press Enter to start the main simulation.
- The simulation will evolve the cars' behaviors over several generations using the NEAT algorithm.
- During the simulation, you can see the fitness of all the cars alive. Press the L button to hide or show this information.
- The simulation can be interrupted and saved at any point by pressing the Esc key.
- The simulation will also complete automatically after 10 generations.
- A new generation starts every 6 to 8 laps, depending on the number of cars alive.

### Run the Graph Generator

- After the simulation completes, press Enter to generate and display performance graphs.
- This step runs the GraphGenerator tool in a separate process, allowing you to visualize the progress and performance of the cars.

## How Cars Earn or Lose Fitness

### Fitness Gain

- **Lap Completion:** Cars gain fitness based on the speed of lap completion. The faster a car completes a lap, the more fitness it gains.
  - Fitness increment formula: `genome.fitness += 1000 / lap_time`

### Fitness Penalty

- **Heading Deviation:** Cars lose fitness if their heading deviation is too high. The penalty is proportional to the heading difference but reduced to half.
  - Fitness penalty formula: `genome.fitness -= min(heading_diff / 2, genome.fitness)`

## Notes

- The `race_results.csv` file will be generated to store the results of the simulation.
- The `track.png` file will be saved in the `assets` directory.
- The population will be saved in a `population.pkl` file for continuity between sessions.

## Troubleshooting

If you encounter any issues running the scripts, ensure all required libraries are installed and your environment is properly set up. For any errors related to file paths or missing assets, check the paths specified in the scripts.

## License

This project is open-source and available under the [MIT License](LICENSE).
