import pygame
import pygame_gui
import tkinter as tk
from tkinter import messagebox
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080  # Dimensions of the window
BACKGROUND_COLOR = (2, 105, 31)  # Background color (green)
PATH_COLOR = (128, 128, 128)  # Path color (gray)
OVERLAP = 5  # Overlap for a uniform stroke
TEXT_COLOR = (128, 128, 128)  # Text color (gray)
LINE_WIDTH = 20  # Width of the white line

# Configure the Pygame window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Track Creator")
screen.fill(BACKGROUND_COLOR)

# Initialize Pygame_gui
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create a button to close the window
close_window_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, WINDOW_HEIGHT - 60), (140, 50)),
    text='Close',
    manager=manager
)

# Create a button to clear the map
clear_map_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WINDOW_WIDTH - 300, WINDOW_HEIGHT - 60), (140, 50)),
    text='Clear',
    manager=manager
)

# Create a label for the slider
brush_width_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 110), (300, 50)),
    text='Brush width',
    manager=manager
)

# Create a slider to adjust the brush width
brush_width_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 60), (300, 50)),
    start_value=135,
    value_range=(120, 150),
    manager=manager
)

# Create a button to hide/show the UI
toggle_ui_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60), (140, 50)),
    text='Hide UI',
    manager=manager
)

# Variables for drawing
drawing = False  # Indicates if drawing is in progress
path_segments = []  # Segments of the drawn path
brush_width = 135  # Initial brush width
ui_visible = True  # UI visibility state

# Variables for the white line
line_x = WINDOW_WIDTH // 2  # X position of the line
line_y = WINDOW_HEIGHT // 2  # Y position of the line
line_angle = 0  # Rotation angle of the line

# Variables to keep track of key presses
keys_pressed = {
    pygame.K_LEFT: False,
    pygame.K_RIGHT: False,
    pygame.K_UP: False,
    pygame.K_DOWN: False,
    pygame.K_r: False
}

# Font for the text
font = pygame.font.Font(None, 36)

# Function to save the image
def save_image():
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the path to the assets folder
    assets_dir = os.path.join(script_dir, "assets")
    # Create the assets folder if it doesn't exist
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    # Define the destination file name
    filename = os.path.join(assets_dir, "track.png")
    # Save the image
    pygame.image.save(screen, filename)
    # Show a success message
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    messagebox.showinfo("Success", f"Image saved as {filename}")
    root.destroy()
    # Set running to False to close the game
    global running
    running = False

# Function to check if the mouse is over a UI element
def is_mouse_over_ui(mouse_pos):
    if not ui_visible:
        return False
    ui_elements = [
        close_window_button.rect,
        clear_map_button.rect,
        brush_width_label.rect,
        brush_width_slider.rect,
        toggle_ui_button.rect
    ]
    return any(element.collidepoint(mouse_pos) for element in ui_elements)

# Function to draw the rotated white line
def draw_rotated_line(surface, color, x, y, width, height, angle):
    line_surface = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a surface for the line
    line_surface.fill(color)  # Fill the surface with the specified color
    rotated_surface = pygame.transform.rotate(line_surface, angle)  # Rotate the surface
    rect = rotated_surface.get_rect(center=(x, y))  # Get the rectangle of the rotated surface
    surface.blit(rotated_surface, rect.topleft)  # Draw the rotated surface on the main surface

# Main Pygame loop
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0  # Keep the frame rate at 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if not is_mouse_over_ui(event.pos):
                    drawing = True  # Start drawing
                    path_segments.append([event.pos])  # Add a new segment
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                drawing = False  # Stop drawing
        elif event.type == pygame.MOUSEMOTION:
            if drawing and not is_mouse_over_ui(event.pos):
                path_segments[-1].append(event.pos)  # Add the new position to the current segment
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == close_window_button:
                    running = False  # Close the window
                elif event.ui_element == clear_map_button:
                    path_segments = []  # Clear the path segments
                elif event.ui_element == toggle_ui_button:
                    ui_visible = not ui_visible  # Toggle UI visibility
                    if ui_visible:
                        toggle_ui_button.set_text('Hide UI')
                    else:
                        toggle_ui_button.set_text('Show UI')
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == brush_width_slider:
                    brush_width = int(event.value)  # Update the brush width
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                save_image()  # Save the image
            elif event.key == pygame.K_ESCAPE:
                if not ui_visible:
                    ui_visible = True
                    toggle_ui_button.set_text('Hide UI')
            elif event.key in keys_pressed:
                keys_pressed[event.key] = True  # Mark the key as pressed
        elif event.type == pygame.KEYUP:
            if event.key in keys_pressed:
                keys_pressed[event.key] = False  # Mark the key as released

        manager.process_events(event)  # Process UI events

    # Update the position and rotation of the white line based on key presses
    if keys_pressed[pygame.K_LEFT]:
        line_x -= 10
    if keys_pressed[pygame.K_RIGHT]:
        line_x += 10
    if keys_pressed[pygame.K_UP]:
        line_y -= 10
    if keys_pressed[pygame.K_DOWN]:
        line_y += 10
    if keys_pressed[pygame.K_r]:
        line_angle = (line_angle + 15) % 360

    screen.fill(BACKGROUND_COLOR)  # Fill the screen with the background color
    for segment in path_segments:  # Draw the path segments
        if len(segment) > 1:
            for i in range(1, len(segment)):
                pygame.draw.line(screen, PATH_COLOR, segment[i - 1], segment[i], brush_width)  # Draw the path segment
                pygame.draw.circle(screen, PATH_COLOR, segment[i], brush_width // 2)  # Draw circles at segment points
        elif len(segment) == 1:
            pygame.draw.circle(screen, PATH_COLOR, segment[0], brush_width // 2)  # Draw a circle for single points

    # Draw the rotated white line
    draw_rotated_line(screen, (255, 255, 255), line_x, line_y, LINE_WIDTH, brush_width, line_angle)

    if ui_visible:
        manager.update(time_delta)  # Update the UI manager
        manager.draw_ui(screen)  # Draw the UI elements
        # Render the text in the top left corner
        text_surface1 = font.render("Press enter to create the track", True, TEXT_COLOR)
        text_surface2 = font.render("Press esc to show UI when it is hidden", True, TEXT_COLOR)
        screen.blit(text_surface1, (10, 10))
        screen.blit(text_surface2, (10, 50))

    pygame.display.flip()  # Update the display

pygame.quit()  # Quit Pygame
