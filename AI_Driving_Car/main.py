import pygame
import os
import math
import sys
import neat
import csv
import time
import random

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

TRACK = pygame.image.load(os.path.join("Assets", "track.png"))

pygame.font.init()
FONT = pygame.font.SysFont('Arial', 20)

show_leaderboard = True

class Car(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("Assets", "car.png"))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=start_pos)
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        self.lap = True
        self.lap_times = []
        self.current_lap_start_time = 0
        self.time_passed_to_start = 0
        self.completed_laps = 0

    def drive(self):
        self.rect.center += self.vel_vector * 6

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        length = 0

        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        track_width, track_height = TRACK.get_width(), TRACK.get_height()

        while 0 <= x < track_width and 0 <= y < track_height and not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        pygame.draw.line(SCREEN, (255, 255, 254, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2) + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input

    def collision(self):
        length = 40
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False

        if SCREEN.get_at(collision_point_right) == pygame.Color(255, 255, 255) and self.lap:
            self.current_lap_start_time = time.time()
            self.time_passed_to_start = time.time() - self.current_lap_start_time
            self.lap = False

        if SCREEN.get_at(collision_point_right) == pygame.Color(255, 255, 255) and not self.lap and self.time_passed_to_start > 1:
            self.lap = True
            self.lap_times.append(time.time() - self.current_lap_start_time)
            self.completed_laps += 1
            self.current_lap_start_time = time.time()  # Reset for the next lap

        self.time_passed_to_start = time.time() - self.current_lap_start_time

        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)

    def update(self):
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        self.collision()
        self.data()

def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)

def find_starting_line():
    start_positions = []
    for y in range(TRACK.get_height()):
        for x in range(TRACK.get_width()):
            if TRACK.get_at((x, y)) == pygame.Color(255, 255, 255, 255):
                if not TRACK.get_at((x-80, y)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x-80, y))
                elif not TRACK.get_at((x+80, y)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x+80, y))
                elif not TRACK.get_at((x, y-80)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x, y-80))
                elif not TRACK.get_at((x, y + 80)) == pygame.Color(255, 255, 255, 255):
                    start_positions.append((x, y + 80))
                else:
                    start_positions.append((x, y))
    return start_positions

def update_leaderboard(cars, ge):
    if not show_leaderboard:
        return
    leaderboard_surface = pygame.Surface((300, SCREEN_HEIGHT))
    leaderboard_surface.fill((0, 0, 0))
    for i, genome in enumerate(ge):
        car_status = "N/A" if not cars[i].sprite.alive else "Alive"
        text = FONT.render(f"Car {i+1}: {car_status} - Fitness: {genome.fitness}", True, (255, 255, 255))
        leaderboard_surface.blit(text, (10, 30 * i))
    SCREEN.blit(leaderboard_surface, (SCREEN_WIDTH - 300, 0))

def eval_genomes(genomes, config):
    global cars, ge, nets, pop, run_generation, total_laps

    cars = []
    ge = []
    nets = []

    start_positions = find_starting_line()
    if not start_positions:
        raise Exception("No starting line found on the track image")

    for genomes_id, genome in genomes:
        start_pos = random.choice(start_positions)
        cars.append(pygame.sprite.GroupSingle(Car(start_pos)))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_results_to_csv()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_results_to_csv()
                    pop.reporters.end_generation(pop.generation)
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_l:  # Press 'L' to toggle leaderboard
                    global show_leaderboard
                    show_leaderboard = not show_leaderboard

        SCREEN.blit(TRACK, (0, 0))

        if len(cars) == 0:
            save_results_to_csv()
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0

        for car in cars:
            car.draw(SCREEN)
            car.update()

        update_leaderboard(cars, ge)
        pygame.display.update()

        # Check if total laps reached a multiple of 5
        total_laps = sum(car.sprite.completed_laps for car in cars)
        if total_laps % 5 == 0 and total_laps > 0:
            save_results_to_csv()
            break

def save_results_to_csv():
    global run_generation
    with open('race_results.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([f"Run Generation {run_generation}"])
        writer.writerow(["Car ID", "Lap Number", "Lap Time", "Fitness"])
        for i, car in enumerate(cars):
            for lap_num, lap_time in enumerate(car.sprite.lap_times):
                rounded_lap_time = round(lap_time, 2)
                writer.writerow([i+1, lap_num + 1, rounded_lap_time, ge[i].fitness])
    run_generation += 1

def run(config_path):
    global pop, run_generation

    # Check if the race_results.csv file exists and delete it if it does
    if os.path.exists('race_results.csv'):
        os.remove('race_results.csv')

    run_generation = 0

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
