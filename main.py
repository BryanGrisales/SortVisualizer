import pygame
import random
import pygame_gui
import time

# Initialize Pygame
pygame.init()

# Screen setup
WINDOW_SIZE = 600
WINDOW = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Sorting Algorithm Visualization')

# Constants
RECT_WIDTH = 20
FPS = 60

# Colors
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
GREY = (170, 170, 170)
LIGHT_BLUE = (64, 224, 208)
WHITE = (255, 255, 255)

# Font
pygame.font.init()
FONT = pygame.font.SysFont('Arial', 20)

def create_gui_manager():
    """Creates a new Pygame GUI Manager."""
    return pygame_gui.UIManager((WINDOW_SIZE, WINDOW_SIZE))

def create_rectangles():
    """Creates a list of rectangles with random heights."""
    num_rectangles = WINDOW_SIZE // RECT_WIDTH - 5
    rectangles = []
    heights = set()
    
    for i in range(5, num_rectangles):
        height = random.randint(20, 500)
        while height in heights:
            height = random.randint(20, 500)
        
        heights.add(height)
        rect = Rectangle(PURPLE, i * RECT_WIDTH, height)
        rectangles.append(rect)
    
    return rectangles

def draw_rectangles(rectangles):
    """Draws all rectangles on the screen."""
    WINDOW.fill(GREY)

    for rect in rectangles:
        pygame.draw.rect(WINDOW, rect.color, (rect.x, WINDOW_SIZE - rect.height, rect.width, rect.height))
        pygame.draw.line(WINDOW, BLACK, (rect.x, WINDOW_SIZE), (rect.x, WINDOW_SIZE - rect.height))
        pygame.draw.line(WINDOW, BLACK, (rect.x + rect.width, WINDOW_SIZE), (rect.x + rect.width, WINDOW_SIZE - rect.height))
        pygame.draw.line(WINDOW, BLACK, (rect.x, WINDOW_SIZE - rect.height), (rect.x + rect.width, WINDOW_SIZE - rect.height))

def selection_sort(rectangles):
    """Generator for performing selection sort and visualizing it."""
    num_rectangles = len(rectangles)
    comparisons, swaps = 0, 0

    for i in range(num_rectangles):
        min_index = i
        rectangles[i].set_smallest()

        for j in range(i + 1, num_rectangles):
            rectangles[j].select()
            draw_rectangles(rectangles)
            comparisons += 1

            if rectangles[j].height < rectangles[min_index].height:
                rectangles[min_index].unselect()
                min_index = j
            
            rectangles[min_index].set_smallest()
            draw_rectangles(rectangles)
            rectangles[j].unselect()

            yield comparisons, swaps
        
        # Swap
        if min_index != i:
            rectangles[i].x, rectangles[min_index].x = rectangles[min_index].x, rectangles[i].x
            rectangles[i], rectangles[min_index] = rectangles[min_index], rectangles[i]
            swaps += 1

        rectangles[min_index].unselect()
        rectangles[i].set_sorted()

        draw_rectangles(rectangles)
        yield comparisons, swaps

def bubble_sort(rectangles):
    """Generator for performing bubble sort and visualizing it."""
    n = len(rectangles)
    comparisons, swaps = 0, 0

    for i in range(n):
        for j in range(0, n-i-1):
            rectangles[j].select()
            rectangles[j+1].select()
            draw_rectangles(rectangles)
            comparisons += 1

            if rectangles[j].height > rectangles[j+1].height:
                rectangles[j].x, rectangles[j+1].x = rectangles[j+1].x, rectangles[j].x
                rectangles[j], rectangles[j+1] = rectangles[j+1], rectangles[j]
                swaps += 1
            
            draw_rectangles(rectangles)
            rectangles[j].unselect()
            rectangles[j+1].unselect()

            yield comparisons, swaps

        rectangles[n-i-1].set_sorted()
        draw_rectangles(rectangles)
        yield comparisons, swaps

def display_text(text, y, size):
    """Displays a text message on the screen."""
    font = pygame.font.SysFont('Arial', size)
    text_rect = pygame.Rect(0, y - size // 2, WINDOW_SIZE, size)
    pygame.draw.rect(WINDOW, GREY, text_rect)  # Clear the area with the background color
    rendered_text = font.render(text, True, BLACK)
    text_rect = rendered_text.get_rect(center=(WINDOW_SIZE / 2, y))
    WINDOW.blit(rendered_text, text_rect)

def handle_events(manager, speed_slider):
    """Handles Pygame events and updates the UI manager."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return 'toggle_sorting'
            if event.key == pygame.K_r:
                return 'reset'
            if event.key == pygame.K_1:
                return 'selection_sort'
            if event.key == pygame.K_2:
                return 'bubble_sort'
            if event.key == pygame.K_q:
                return False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_button:
                    return 'menu'  # Ensure this returns 'menu'

        manager.process_events(event)
    
    return True

class Rectangle: 
    def __init__(self, color, x, height):
        self.color = color
        self.x = x
        self.width = RECT_WIDTH
        self.height = height
    
    def select(self):
        self.color = BLUE

    def unselect(self):
        self.color = PURPLE
    
    def set_smallest(self):
        self.color = LIGHT_BLUE

    def set_sorted(self):
        self.color = GREEN

def reset_rectangles():
    """Resets the rectangles and related variables."""
    rectangles = create_rectangles()
    return rectangles, 0, 0

def main():
    global manager, speed_slider, reset_button  # Make sure they are globally accessible
    rectangles, comparisons, swaps = reset_rectangles()
    sorting_generator = None
    draw_rectangles(rectangles)  # Initial drawing of rectangles

    run = True
    sorting = False
    speed = FPS
    clock = pygame.time.Clock()
    last_sort_time = time.time()
    algorithm = None
    show_menu = True

    # GUI Manager Initialization
    manager = create_gui_manager()
    
    # Create the GUI elements
    speed_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((150, 500), (300, 25)),
        start_value=30,
        value_range=(1, 60),
        manager=manager
    )
    reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((10, 10), (70, 30)),  # Adjusted size to make it smaller
        text='Menu',
        manager=manager
    )
    
    # Hide the speed slider initially
    speed_slider.hide()

    while run:
        time_delta = clock.tick(FPS) / 1000.0

        if sorting and sorting_generator:
            current_time = time.time()
            if current_time - last_sort_time > (1.0 / speed):
                try:
                    comparisons, swaps = next(sorting_generator)
                    last_sort_time = current_time
                except StopIteration:
                    sorting = False
            draw_rectangles(rectangles)  # Draw only when sorting steps occur

        if not show_menu:
            draw_rectangles(rectangles)
            display_text('Sorting Algorithm: {}'.format(algorithm), 30, 30)
            display_text(f'Comparisons: {comparisons} Swaps: {swaps}', 60, 20)
            display_text('Press SPACE to start/pause, R to reset, Q to quit', 90, 20)
            manager.update(time_delta)
            manager.draw_ui(WINDOW)

            # Show the speed slider during sorting
            speed_slider.show()

        else:
            # Display menu to select algorithm
            WINDOW.fill(GREY)
            display_text('Select Sorting Algorithm', 30, 30)
            display_text('Press 1 for Selection Sort', 60, 20)
            display_text('Press 2 for Bubble Sort', 90, 20)
            display_text('Press R to Reset, Q to Quit', 120, 20)
            manager.update(time_delta)
            manager.draw_ui(WINDOW)

            # Hide the speed slider in the menu
            speed_slider.hide()

        result = handle_events(manager, speed_slider)
        if result == 'toggle_sorting':
            sorting = not sorting
        elif result == 'reset':
            sorting = False  # Stop the automatic sorting
            rectangles, comparisons, swaps = reset_rectangles()
            if algorithm == "Selection Sort":
                sorting_generator = selection_sort(rectangles)
            elif algorithm == "Bubble Sort":
                sorting_generator = bubble_sort(rectangles)
            draw_rectangles(rectangles)
        elif result == 'selection_sort':
            rectangles, comparisons, swaps = reset_rectangles()
            sorting_generator = selection_sort(rectangles)
            algorithm = "Selection Sort"
            show_menu = False
        elif result == 'bubble_sort':
            rectangles, comparisons, swaps = reset_rectangles()
            sorting_generator = bubble_sort(rectangles)
            algorithm = "Bubble Sort"
            show_menu = False
        elif result == 'menu':  # Handle menu button click
            show_menu = True
            sorting = False
            rectangles, comparisons, swaps = reset_rectangles()
            sorting_generator = None
            manager = create_gui_manager()  # Recreate GUI manager
            speed_slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((150, 500), (300, 25)),
                start_value=30,
                value_range=(1, 60),
                manager=manager
            )
            reset_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((10, 10), (70, 30)),  # Adjusted size to make it smaller
                text='Menu',
                manager=manager
            )
            # Hide the speed slider in the menu
            speed_slider.hide()
        elif result is False:
            run = False  # Exit the main loop

        speed = speed_slider.get_current_value()

        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
