import pygame
import pygame_gui
import tkinter as tk
from tkinter import messagebox
import os

# Inizializzazione di Pygame
pygame.init()

# Costanti
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
BACKGROUND_COLOR = (2, 105, 31)
PATH_COLOR = (128, 128, 128)
OVERLAP = 5  # Sovrapposizione per ottenere un tratto omogeneo
TEXT_COLOR = (128, 128, 128)  # Grigio
LINE_WIDTH = 20  # Larghezza della linea bianca

# Configurazione della finestra Pygame
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Track Creator")
screen.fill(BACKGROUND_COLOR)

# Inizializzazione di Pygame_gui
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Creazione del bottone per chiudere la finestra
close_window_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, WINDOW_HEIGHT - 60), (140, 50)),
    text='Close',
    manager=manager
)

# Creazione del bottone per pulire la mappa
clear_map_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WINDOW_WIDTH - 300, WINDOW_HEIGHT - 60), (140, 50)),
    text='Clear',
    manager=manager
)

# Creazione del testo per lo slider
brush_width_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 110), (300, 50)),
    text='Brush width',
    manager=manager
)

# Creazione dello slider per regolare la larghezza del pennello
brush_width_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 60), (300, 50)),
    start_value=125,
    value_range=(100, 150),
    manager=manager
)

# Creazione del bottone per nascondere/mostrare la UI
toggle_ui_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60), (140, 50)),
    text='Hide UI',
    manager=manager
)

# Variabili per il disegno
drawing = False
path_segments = []
brush_width = 125  # Larghezza iniziale del pennello
ui_visible = True  # Stato di visibilità dell'interfaccia utente

# Variabili per la linea bianca
line_x = WINDOW_WIDTH // 2
line_y = WINDOW_HEIGHT // 2
line_angle = 0  # Angolo di rotazione della linea

# Variabili per tenere traccia dei tasti premuti
keys_pressed = {
    pygame.K_LEFT: False,
    pygame.K_RIGHT: False,
    pygame.K_UP: False,
    pygame.K_DOWN: False,
    pygame.K_r: False
}

# Font per il testo
font = pygame.font.Font(None, 36)

# Funzione per salvare l'immagine
def save_image():
    # Ottieni il percorso dello script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Definisci il percorso della cartella assets
    assets_dir = os.path.join(script_dir, "assets")
    # Crea la cartella assets se non esiste
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    # Definisci il nome del file di destinazione
    filename = os.path.join(assets_dir, "track.png")
    # Salva l'immagine
    pygame.image.save(screen, filename)
    # Mostra un messaggio di successo
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale di Tkinter
    messagebox.showinfo("Success", f"Image saved as {filename}")
    root.destroy()
    # Imposta running su False per chiudere il gioco
    global running
    running = False

# Funzione per verificare se il mouse è sopra un elemento UI
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

# Funzione per disegnare la linea bianca ruotata
def draw_rotated_line(surface, color, x, y, width, height, angle):
    line_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    line_surface.fill(color)
    rotated_surface = pygame.transform.rotate(line_surface, angle)
    rect = rotated_surface.get_rect(center=(x, y))
    surface.blit(rotated_surface, rect.topleft)

# Loop principale di Pygame
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0  # Mantiene il framerate a 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Sinistro del mouse
                if not is_mouse_over_ui(event.pos):
                    drawing = True
                    path_segments.append([event.pos])
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Sinistro del mouse
                drawing = False
        elif event.type == pygame.MOUSEMOTION:
            if drawing and not is_mouse_over_ui(event.pos):
                path_segments[-1].append(event.pos)
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == close_window_button:
                    running = False
                elif event.ui_element == clear_map_button:
                    path_segments = []
                elif event.ui_element == toggle_ui_button:
                    ui_visible = not ui_visible
                    if ui_visible:
                        toggle_ui_button.set_text('Hide UI')
                    else:
                        toggle_ui_button.set_text('Show UI')
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == brush_width_slider:
                    brush_width = int(event.value)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                save_image()
            elif event.key == pygame.K_ESCAPE:
                if not ui_visible:
                    ui_visible = True
                    toggle_ui_button.set_text('Hide UI')
            elif event.key in keys_pressed:
                keys_pressed[event.key] = True
        elif event.type == pygame.KEYUP:
            if event.key in keys_pressed:
                keys_pressed[event.key] = False

        manager.process_events(event)

    # Aggiorna posizione e rotazione della linea bianca in base ai tasti premuti
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

    screen.fill(BACKGROUND_COLOR)
    for segment in path_segments:
        if len(segment) > 1:
            for i in range(1, len(segment)):
                pygame.draw.line(screen, PATH_COLOR, segment[i - 1], segment[i], brush_width)
                pygame.draw.circle(screen, PATH_COLOR, segment[i], brush_width // 2)
        elif len(segment) == 1:
            pygame.draw.circle(screen, PATH_COLOR, segment[0], brush_width // 2)

    # Disegno della linea bianca ruotata
    draw_rotated_line(screen, (255, 255, 255), line_x, line_y, LINE_WIDTH, brush_width, line_angle)

    if ui_visible:
        manager.update(time_delta)
        manager.draw_ui(screen)
        # Render del testo in alto a sinistra
        text_surface1 = font.render("Press enter to create the track", True, TEXT_COLOR)
        text_surface2 = font.render("Press esc to show UI when it is hidden", True, TEXT_COLOR)
        screen.blit(text_surface1, (10, 10))
        screen.blit(text_surface2, (10, 50))

    pygame.display.flip()

pygame.quit()
