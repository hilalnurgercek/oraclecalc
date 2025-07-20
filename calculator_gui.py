import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 700
BG_COLOR = pygame.Color("#519381")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OracleCalc")

# Represents each button visually and functionally
class Button:
    def __init__(self, image_path, inv_image_path, position, symbol, size=(70, 70)):

        # Normal and inverted images for button states to have the illusion of being pressed
        raw_image = pygame.image.load(image_path).convert_alpha()
        raw_inv_image = pygame.image.load(inv_image_path).convert_alpha()

        self.image = pygame.transform.smoothscale(raw_image, size)
        self.inv_image = pygame.transform.smoothscale(raw_inv_image, size)

        self.rect = self.image.get_rect(topleft=position)
        self.symbol = symbol
        self.is_pressed = False

    # Draws the button on the given surface
    # If the button is pressed, it draws the inverted image
    # Otherwise, it draws the normal image
    def draw_button(self, surface):
        if self.is_pressed:
            surface.blit(self.inv_image, self.rect.topleft)
        else:
            surface.blit(self.image, self.rect.topleft)

    # Checks if the button is clicked based on the mouse position
    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            x, y = pos[0] - self.rect.x, pos[1] - self.rect.y
            if self.image.get_at((x, y)).a > 0:
                return True
        return False


# Manages the entire calculator GUI, state, and logic
class NumberDisplayGUI:
    def __init__(self):
        self.current_expression = ""
        self.latest_number = None
        self.awaiting_audio_number = False

        # Load the calculator screen image and scale it
        self.screen_image = pygame.image.load('Img_new/calc_screen.png').convert_alpha()
        scale_factor = 0.18
        w, h = self.screen_image.get_size()
        self.screen_size = (int(w * scale_factor), int(h * scale_factor))
        self.screen_image = pygame.transform.smoothscale(self.screen_image, self.screen_size)

        # Load number and operator images for display
        self.display_images = {}
        for digit in '0123456789':
            path = f'Img_new/calc_numbers/{digit}.png'
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (40, 60))
            self.display_images[digit] = img

        symbol_to_filename = {
            '+': 'add',
            '-': 'subt',
            'x': 'mult',
            '/': 'div'
        }

        for symbol, filename in symbol_to_filename.items():
            path = f'Img_new/calc_numbers/{filename}.png'
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (40, 60))
            self.display_images[symbol] = img

        # Load button setup and layout
        self.buttons = []
        self.load_buttons()
        self.layout_positions()

    # Loads button images and their inverted versions 
    def load_buttons(self):
        symbol_to_filename = {
            '+': 'add', '-': 'subt', 'x': 'mult', '/': 'div', '=': 'eq', 'C': 'C'
        }
        self.symbol_to_image = {}

        for label in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', 'x', '/', 'C', '=']:
            filename = symbol_to_filename.get(label, label)
            path = f'Img_new/newf/{filename}.png'
            inv_path = f'Img_new/calc_inv/{filename}.png'
            self.symbol_to_image[label] = (path, inv_path)

   # Positions buttons in a grid layout
    def layout_positions(self):
        screen_x = (WIDTH - self.screen_size[0]) // 2
        self.screen_pos = (screen_x, 40)

        btn_size = (70, 70)
        spacing = 20
        grid_cols = 4
        grid_rows = 4
        # Calculates the leftmost x-pos of the button grid, centering horizontally
        start_x = (WIDTH - (btn_size[0]*grid_cols + spacing*(grid_cols-1))) // 2
        # Calculates the topmost y-pos of the button grid, placing it below the screen
        start_y = self.screen_pos[1] + self.screen_size[1] + 40

        numbers = ['7','8','9','+',
                   '4','5','6','-',
                   '1','2','3','x',
                   'C','0','=','/']

        self.buttons = []
        for idx, symbol in enumerate(numbers):
            col = idx % grid_cols
            row = idx // grid_cols
            x = start_x + col * (btn_size[0] + spacing)
            y = start_y + row * (btn_size[1] + spacing)
            image_path, inv_path = self.symbol_to_image[symbol]
            # Create a Button object with the image paths, position, symbol, and size
            self.buttons.append(Button(image_path, inv_path, (x, y), symbol, size=btn_size))

    # Draws the calculator screen and buttons on the given surface
    def draw(self, surface):
        surface.fill(BG_COLOR)
        surface.blit(self.screen_image, self.screen_pos)

        text_y = self.screen_pos[1] + (self.screen_size[1] // 2) - 30

        # Available width inside the screen image
        available_width = self.screen_size[0] - 40  # 20px padding on each side

        # Insert error.png if the current expression is "Error"
        if self.current_expression == "Error":
            error_img = pygame.image.load('Img_new/error.png').convert_alpha()
            orig_w, orig_h = error_img.get_size()
            scale_factor = 0.15  
            new_size = (int(orig_w * scale_factor), int(orig_h * scale_factor))

            error_img = pygame.transform.smoothscale(error_img, new_size)
            offset_x = 22  # moving more to the right
            offset_y = -22  # moving slightly upward

            error_x = self.screen_pos[0] + self.screen_size[0] - error_img.get_width() - offset_x
            error_y = text_y + offset_y

            surface.blit(error_img, (error_x, error_y))

        else:
            # rendered_parts => a tuple that contains the char itself and the corresponding image
            rendered_parts = []
            for char in self.current_expression:
                img = self.display_images[char]
                rendered_parts.append((char, img))

            total_width = sum(img.get_width() + 3 for _, img in rendered_parts)

            # If the total width exceeds the available width, remove parts from the start
            while total_width > available_width and len(rendered_parts) > 1:
                removed_char, removed_img = rendered_parts.pop(0)
                total_width -= (removed_img.get_width() + 3)

            text_x = self.screen_pos[0] + self.screen_size[0] - total_width - 20

            for _, img in rendered_parts:
                surface.blit(img, (text_x, text_y))
                text_x += img.get_width() + 3

        # Well, finally drawing the buttons
        for button in self.buttons:
            button.draw_button(surface)

    # Updates the number in the display when a number is recognized from audio input
    def update_number(self, number):
        print(f"Audio number stored: {number}")
        self.latest_number = str(number)
        self.awaiting_audio_number = True

    # Handles mouse clicks on the buttons and updates the display accordingly
    def handle_click(self, pos):
        for button in self.buttons:
            if button.is_clicked(pos):
                button.is_pressed = True
                self.draw(screen)
                pygame.display.flip()
                pygame.time.delay(100)  # 100ms visual press effect
                button.is_pressed = False

                symbol = button.symbol
                # If the current expression is "Error", clear the display
                if self.current_expression == "Error":
                    self.clear_display()
                if symbol == '=':
                    self.on_enter_pressed()
                elif symbol == 'C':
                    self.clear_display()
                else:
                    self.current_expression += symbol
                break

    # Handles the Enter key press to evaluate the current expression
    def on_enter_pressed(self):
        if self.awaiting_audio_number and self.latest_number is not None:
            # If waiting for audio number, replace display with latest number
            print(f"Audio number inserted: {self.latest_number}")
            self.current_expression = str(self.latest_number)
            self.draw(screen)
            # Refresh the display to show the latest number
            pygame.display.flip()

            self.awaiting_audio_number = False
            self.latest_number = None
        else:
            # If not waiting for audio number, evaluate the current expression
            try:
                expression = self.current_expression.replace('x', '*')
                result = eval(expression)
                self.current_expression = str(result)
            except Exception as e:
                print(f"Evaluation error: {e}")
                self.current_expression = "Error"

    # Clears the current expression in the display
    def clear_display(self):
        self.current_expression = ""

    # Runs the main loop of the GUI
    def run(self):
        # a clock to control the frame rate
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw(screen) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                # checks if the event was mouse click
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            pygame.display.flip()
            clock.tick(30)

        # Release resources and exit
        pygame.quit()
        sys.exit()


# Main entry point to run the GUI (if needed)
if __name__ == "__main__":
    gui = NumberDisplayGUI()
    gui.run()
