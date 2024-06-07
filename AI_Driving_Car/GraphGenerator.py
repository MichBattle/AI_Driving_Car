import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Function to read data from CSV
def read_data(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    generations = []
    data = {'Run': [], 'Fitness': [], 'LapTime': []}

    for line in lines:
        if line.startswith('Run Generation'):
            generation = int(line.strip().split()[-1])
            generations.append(generation)
        elif line.startswith('Car ID'):
            continue
        else:
            parts = line.strip().split(',')
            lap_time = float(parts[2])
            fitness = float(parts[3])
            data['Run'].append(generation)
            data['LapTime'].append(lap_time)
            data['Fitness'].append(fitness)

    df = pd.DataFrame(data)
    return df

# Read the data from CSV
df = read_data('race_results.csv')

# Calculate additional statistics for the plots
df['AverageFitness'] = df.groupby('Run')['Fitness'].transform('mean')
df['BestFitness'] = df.groupby('Run')['Fitness'].transform('max')
df['AverageLapTime'] = df.groupby('Run')['LapTime'].transform('mean')
df['BestLapTime'] = df.groupby('Run')['LapTime'].transform('min')

# Count the number of cars that survived each run
df['Survivors'] = df.groupby('Run')['Run'].transform('count')

# Create the main window
root = tk.Tk()
root.title("Performance Improvement")

def plot_average_fitness():
    fig, ax = plt.subplots()
    ax.plot(df['Run'].unique(), df.groupby('Run')['AverageFitness'].mean(), marker='o')
    ax.set_title('Average Fitness per Generation')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Average Fitness')
    show_plot(fig)

def plot_average_lap_time():
    fig, ax = plt.subplots()
    ax.plot(df['Run'].unique(), df.groupby('Run')['AverageLapTime'].mean(), marker='o')
    ax.set_title('Average Lap Time per Generation')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Average Lap Time (s)')
    show_plot(fig)

def plot_best_fitness():
    fig, ax = plt.subplots()
    ax.plot(df['Run'].unique(), df.groupby('Run')['BestFitness'].max(), marker='o')
    ax.set_title('Best Fitness per Generation')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best Fitness')
    show_plot(fig)

def plot_best_lap_time():
    fig, ax = plt.subplots()
    ax.plot(df['Run'].unique(), df.groupby('Run')['BestLapTime'].min(), marker='o')
    ax.set_title('Best Lap Time per Generation')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Best Lap Time (s)')
    show_plot(fig)

def plot_survivors_per_run():
    fig, ax = plt.subplots()
    ax.plot(df['Run'].unique(), df.groupby('Run')['Survivors'].max(), marker='o')
    ax.set_title('Number of Cars Survived per Generation')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Number of Cars')
    show_plot(fig)

def show_plot(fig):
    for widget in frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X)

button1 = ttk.Button(button_frame, text="Average Fitness per Generation", command=plot_average_fitness)
button1.pack(side=tk.LEFT, padx=5, pady=5)

button2 = ttk.Button(button_frame, text="Average Lap Time per Generation", command=plot_average_lap_time)
button2.pack(side=tk.LEFT, padx=5, pady=5)

button3 = ttk.Button(button_frame, text="Best Fitness per Generation", command=plot_best_fitness)
button3.pack(side=tk.LEFT, padx=5, pady=5)

button4 = ttk.Button(button_frame, text="Best Lap Time per Generation", command=plot_best_lap_time)
button4.pack(side=tk.LEFT, padx=5, pady=5)

button5 = ttk.Button(button_frame, text="Number of Cars Survived per Generation", command=plot_survivors_per_run)
button5.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()
