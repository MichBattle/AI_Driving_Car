import pygame
import os
import math
import sys
import neat
import csv
import time
import random
import pickle
import subprocess

pygame.init()  # Initialize all imported pygame modules

info = pygame.display.Info()  # Get display information
SCREEN_WIDTH = info.current_w  # Get the current width of the screen
SCREEN_HEIGHT = info.current_h  # Get the current height of the screen
SCREEN = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT))  # Set the display mode with the current width and height

TRACK = pygame.image.load(os.path.join("Assets", "track.png"))  # Load the track image from the Assets folder

pygame.font.init()  # Initialize the font module
FONT = pygame.font.SysFont('Arial', 20)  # Set the font to Arial with size 20

show_leaderboard = True  # Flag to show or hide the leaderboard


class Car(pygame.sprite.Sprite):  # Define the Car class inheriting from pygame's Sprite class
    def __init__(self, start_pos):
        super().__init__()  # Initialize the parent Sprite class
        self.original_image = pygame.image.load(os.path.join("Assets", "car.png"))  # Load the car image
        self.image = self.original_image  # Set the current image to the original image
        self.rect = self.image.get_rect(center=start_pos)  # Set the position of the car
        self.vel_vector = pygame.math.Vector2(0.8, 0)  # Set the initial velocity vector
        self.initial_heading = self.vel_vector.angle_to(pygame.math.Vector2(1, 0))  # Track initial heading
        self.angle = 0  # Initial angle
        self.rotation_vel = 5  # Rotation velocity
        self.direction = 0  # Initial direction
        self.alive = True  # Flag to check if the car is alive
        self.radars = []  # List to store radar data
        self.lap = True  # Flag to indicate if a lap is completed
        self.lap_times = []  # List to store lap times
        self.current_lap_start_time = 0  # Start time of the current lap
        self.time_passed_to_start = 0  # Time passed to start
        self.completed_laps = 0  # Number of completed laps

    def drive(self):  # Method to drive the car
        self.rect.center += self.vel_vector * 6  # Update the position based on the velocity

    def rotate(self):  # Method to rotate the car
        if self.direction == 1:  # Rotate left
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:  # Rotate right
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)  # Rotate and scale the image
        self.rect = self.image.get_rect(center=self.rect.center)  # Update the rectangle's position

    def radar(self, radar_angle):  # Method to detect objects using radar
        length = 0  # Initial radar length

        x = int(self.rect.center[0])  # Starting x position of radar
        y = int(self.rect.center[1])  # Starting y position of radar

        track_width, track_height = TRACK.get_width(), TRACK.get_height()  # Get the width and height of the track

        # Extend radar line until it hits a border or a specific color
        while 0 <= x < track_width and 0 <= y < track_height and not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31,
                                                                                                           255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        pygame.draw.line(SCREEN, (255, 255, 254, 255), self.rect.center, (x, y), 1)  # Draw the radar line
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)  # Draw the radar end point

        dist = int(math.sqrt(
            math.pow(self.rect.center[0] - x, 2) + math.pow(self.rect.center[1] - y, 2)))  # Calculate the distance

        self.radars.append([radar_angle, dist])  # Append the radar data

    def data(self):  # Method to get radar data
        input = [0, 0, 0, 0, 0]  # Initialize the input array
        for i, radar in enumerate(self.radars):  # Iterate through the radar data
            input[i] = int(radar[1])  # Store the radar distances
        return input  # Return the input data

    def heading_difference(self):  # Method to calculate heading difference
        current_heading = self.vel_vector.angle_to(pygame.math.Vector2(1, 0))  # Current heading
        return abs(current_heading - self.initial_heading)  # Return the absolute difference

    def collision(self, genome):  # Method to check for collisions
        length = 40  # Length of collision detection lines
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # Check for collision with track border (green color)
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False  # Mark the car as not alive

        # Check for lap completion (white color)
        if SCREEN.get_at(collision_point_right) == pygame.Color(255, 255, 255) and self.lap:
            self.current_lap_start_time = time.time()  # Record the start time of the lap
            self.time_passed_to_start = time.time() - self.current_lap_start_time  # Update the time passed
            self.lap = False  # Mark the lap as not completed

        if SCREEN.get_at(collision_point_right) == pygame.Color(255, 255,
                                                                255) and not self.lap and self.time_passed_to_start > 1:
            self.lap = True  # Mark the lap as completed
            lap_time = time.time() - self.current_lap_start_time  # Calculate the lap time
            self.lap_times.append(lap_time)  # Append the lap time to the list
            self.completed_laps += 1  # Increment the completed laps count
            self.current_lap_start_time = time.time()  # Reset the start time for the next lap

            # Increment fitness based on lap completion speed (the less, the better)
            genome.fitness += 1000 / lap_time  # Update the genome's fitness

        # Adjust the heading deviation penalty
        heading_diff = self.heading_difference()  # Calculate the heading difference
        if heading_diff > 90:
            genome.fitness -= min(heading_diff / 2, genome.fitness)  # Apply a reduced penalty

        self.time_passed_to_start = time.time() - self.current_lap_start_time  # Update the time passed

        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)  # Draw the right collision point
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)  # Draw the left collision point

    def update(self, genome):  # Method to update the car's state
        self.radars.clear()  # Clear previous radar data
        self.drive()  # Move the car
        self.rotate()  # Rotate the car
        for radar_angle in (-60, -30, 0, 30, 60):  # Set radar angles
            self.radar(radar_angle)  # Update radar data
        self.collision(genome)  # Check for collisions
        self.data()  # Get radar data


def remove(index):  # Function to remove a car
    cars.pop(index)  # Remove the car from the cars list
    ge.pop(index)  # Remove the genome from the genomes list
    nets.pop(index)  # Remove the neural network from the nets list


def find_starting_line():  # Function to find the starting line on the track
    start_positions = []  # Initialize the start positions list
    for y in range(TRACK.get_height()):  # Iterate over the track's height
        for x in range(TRACK.get_width()):  # Iterate over the track's width
            if TRACK.get_at((x, y)) == pygame.Color(255, 255, 255, 255):  # Check for the white color
                if not TRACK.get_at((x - 80, y)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x - 80, y))  # Append the start position
                elif not TRACK.get_at((x + 80, y)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x + 80, y))
                elif not TRACK.get_at((x, y - 80)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x, y - 80))
                elif not TRACK.get_at((x, y + 80)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x, y + 80))
                else:
                    start_positions.append((x, y))
    return start_positions  # Return the list of start positions


def update_leaderboard(cars, ge):  # Function to update the leaderboard
    if not show_leaderboard:  # Check if leaderboard should be shown
        return
    leaderboard_surface = pygame.Surface((300, SCREEN_HEIGHT))  # Create a surface for the leaderboard
    leaderboard_surface.fill((0, 0, 0))  # Fill the surface with black color
    for i, genome in enumerate(ge):  # Iterate over the genomes
        car_status = "N/A" if not cars[i].sprite.alive else "Alive"  # Check if the car is alive
        text = FONT.render(f"Car {i + 1}: {car_status} - Fitness: {genome.fitness}", True,
                           (255, 255, 255))  # Render the text
        leaderboard_surface.blit(text, (10, 30 * i))  # Draw the text on the leaderboard surface
    SCREEN.blit(leaderboard_surface, (SCREEN_WIDTH - 300, 0))  # Draw the leaderboard surface on the screen


def reset_laps(cars):  # Function to reset lap information for all cars
    for car in cars:  # Iterate over all cars
        car.sprite.completed_laps = 0  # Reset completed laps count
        car.sprite.lap_times = []  # Clear lap times list


def render_current_lap(cars, generation):  # Function to render current lap information
    text_surface = pygame.Surface((300, 70))  # Create a surface for the text
    text_surface.set_colorkey((0, 0, 0))  # Set black as the transparent color
    text_surface.set_alpha(128)  # Set transparency level

    generation_text = FONT.render(f"Generation Number: {generation}", True,
                                  (169, 169, 169))  # Render the generation number text
    text_surface.blit(generation_text, (10, 10))  # Draw the generation number text on the surface

    current_lap_text = FONT.render(f"Current Lap: {cars[0].sprite.completed_laps + 1}", True,
                                   (169, 169, 169))  # Render the current lap text
    text_surface.blit(current_lap_text, (10, 40))  # Draw the current lap text on the surface

    SCREEN.blit(text_surface, (10, 10))  # Draw the text surface on the screen


def eval_genomes(genomes, config):  # Function to evaluate genomes
    global cars, ge, nets, pop, run_generation, total_laps

    cars = []  # List to store car objects
    ge = []  # List to store genomes
    nets = []  # List to store neural networks

    start_positions = find_starting_line()  # Find the starting line positions
    if not start_positions:  # Check if no starting positions were found
        raise Exception("No starting line found on the track image")

    for genomes_id, genome in genomes:  # Iterate over genomes
        start_pos = random.choice(start_positions)  # Select a random start position
        cars.append(pygame.sprite.GroupSingle(Car(start_pos)))  # Create a car and add it to the cars list
        ge.append(genome)  # Add the genome to the genomes list
        net = neat.nn.FeedForwardNetwork.create(genome, config)  # Create a neural network
        nets.append(net)  # Add the neural network to the nets list
        genome.fitness = 0  # Initialize the fitness value

    run = True  # Flag to control the game loop
    while run:  # Game loop
        for event in pygame.event.get():  # Iterate over events
            if event.type == pygame.QUIT:  # Check if the quit event is triggered
                save_results_to_csv()  # Save the results to CSV
                pygame.quit()  # Quit pygame
                sys.exit()  # Exit the program
            if event.type == pygame.KEYDOWN:  # Check if a key is pressed
                if event.key == pygame.K_ESCAPE:  # Check if the escape key is pressed or 10 generations are completed
                    save_results_to_csv()  # Save the results to CSV
                    pop.reporters.end_generation(pop.config, pop.population, pop.species)  # End the generation
                    pygame.quit()  # Quit pygame
                    sys.exit()  # Exit the program
                if event.key == pygame.K_l:  # Check if the 'L' key is pressed to toggle the leaderboard
                    global show_leaderboard
                    show_leaderboard = not show_leaderboard  # Toggle the leaderboard

        SCREEN.blit(TRACK, (0, 0))  # Draw the track on the screen

        if len(cars) == 0:  # Check if no cars are left
            save_results_to_csv()  # Save the results to CSV
            break  # Break the loop

        for i, car in enumerate(cars):  # Iterate over the cars
            if not car.sprite.alive:  # Check if the car is not alive
                remove(i)  # Remove the car

        for i, car in enumerate(cars):  # Iterate over the cars
            output = nets[i].activate(car.sprite.data())  # Get the neural network output
            if output[0] > 0.7:  # Check if the output indicates a left turn
                car.sprite.direction = 1
            if output[1] > 0.7:  # Check if the output indicates a right turn
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:  # Check if no turn is indicated
                car.sprite.direction = 0

        for i, car in enumerate(cars):  # Iterate over the cars
            car.draw(SCREEN)  # Draw the car on the screen
            car.update(ge[i])  # Update the car's state

        update_leaderboard(cars, ge)  # Update the leaderboard
        render_current_lap(cars, run_generation)  # Render the current lap information
        pygame.display.update()  # Update the display

        total_laps = sum(car.sprite.completed_laps for car in cars)/len(cars)  # Calculate the total laps completed
        if total_laps % 5 == 0 and total_laps > 4:
            save_results_to_csv()  # Save the results to CSV
            save_population()  # Save the population
            reset_laps(cars)  # Reset the laps
            run_generation += 1  # Increment the generation count
            if run_generation >= 9:
                save_results_to_csv()  # Save the results to CSV
                pop.reporters.end_generation(pop.config, pop.population, pop.species)  # End the generation
                pygame.quit()  # Quit pygame
                sys.exit()  # Exit the program
            break  # Break the loop

    # Check if we need to run the graph generator script
    if not any(car.sprite.alive for car in cars):  # Check if no car is alive
        pygame.quit()  # Quit pygame
        try:
            subprocess.run([sys.executable, 'GraphGenerator.py'], check=True)  # Run the graph generator script
        except subprocess.CalledProcessError as e:
            print(f"Error executing GraphGenerator.py: {e}")  # Print the error message
        sys.exit()  # Exit the program


def save_results_to_csv():  # Function to save results to a CSV file
    global run_generation
    with open('race_results.csv', mode='a', newline='') as file:  # Open the CSV file in append mode
        writer = csv.writer(file)  # Create a CSV writer object
        writer.writerow([f"Run Generation {run_generation}"])  # Write the generation number
        writer.writerow(["Car ID", "Lap Number", "Lap Time", "Fitness"])  # Write the header row
        for i, car in enumerate(cars):  # Iterate over the cars
            for lap_num, lap_time in enumerate(car.sprite.lap_times):  # Iterate over the lap times
                rounded_lap_time = round(lap_time, 2)  # Round the lap time to 2 decimal places
                writer.writerow([i + 1, lap_num + 1, rounded_lap_time, ge[i].fitness])  # Write the lap data
    run_generation += 1  # Increment the generation count


def save_population():  # Function to save the population to a file
    with open('population.pkl', 'wb') as f:  # Open the file in write-binary mode
        pickle.dump(pop, f)  # Save the population object to the file


def load_population(config):  # Function to load the population from a file
    global pop
    if os.path.exists('population.pkl'):  # Check if the file exists
        with open('population.pkl', 'rb') as f:  # Open the file in read-binary mode
            pop = pickle.load(f)  # Load the population object from the file
            pop.config = config  # Set the configuration for the population
    else:
        pop = neat.Population(config)  # Create a new population with the given configuration


def run(config_path):  # Function to run the main program
    global run_generation

    # Check if the race_results.csv file exists and delete it if it does
    if os.path.exists('race_results.csv'):
        os.remove('race_results.csv')

    run_generation = 0  # Initialize the generation count

    config = neat.config.Config(  # Load the NEAT configuration
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    load_population(config)  # Load the population

    pop.add_reporter(neat.StdOutReporter(True))  # Add a reporter to output to the console
    stats = neat.StatisticsReporter()  # Create a statistics reporter
    pop.add_reporter(stats)  # Add the statistics reporter

    pop.run(eval_genomes, 50)  # Run the NEAT algorithm for 50 generations


if __name__ == '__main__':  # Check if the script is being run directly
    local_dir = os.path.dirname(__file__)  # Get the directory of the script
    config_path = os.path.join(local_dir, 'config.txt')  # Set the path to the configuration file
    run(config_path)  # Run the main program
