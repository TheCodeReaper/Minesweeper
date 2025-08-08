import pygame
import random
from pygame.locals import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 15 
CELL_SIZE = 30
MARGIN = 50
TOP_MARGIN = 100
BOMB_COUNT = 40  

BG_COLOR = (240, 240, 240)
GRID_COLOR = (200, 200, 200)
HIDDEN_CELL = (200, 200, 200)
REVEALED_CELL = (220, 220, 220)
FLAGGED_CELL = (255, 100, 100)
TEXT_COLORS = [
    None,           
    (0, 0, 255),    
    (0, 128, 0),     
    (255, 0, 0),    
    (0, 0, 128),    
    (128, 0, 0),    
    (0, 128, 128),  
    (0, 0, 0),      
    (128, 128, 128) 
]

class Minesweeper:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.bomb_img = self._create_bomb_icon()
        self.flag_img = self._create_flag_icon()
        
        self.reset_game()
        
    def _create_bomb_icon(self):
        """Create a bomb icon surface"""
        surf = pygame.Surface((CELL_SIZE-4, CELL_SIZE-4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0), (CELL_SIZE//2-2, CELL_SIZE//2-2), CELL_SIZE//3)
        pygame.draw.line(surf, (100, 100, 100), 
                         (CELL_SIZE//2-2, CELL_SIZE//4-2),
                         (CELL_SIZE//2-2, CELL_SIZE//6-2), 3)
        return surf
        
    def _create_flag_icon(self):
        """Create a flag icon surface"""
        surf = pygame.Surface((CELL_SIZE-4, CELL_SIZE-4), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 50, 50), [
            (CELL_SIZE//2-2, 2), 
            (CELL_SIZE//2-2, CELL_SIZE-10),
            (CELL_SIZE-8, CELL_SIZE//2-2)
        ])
        pygame.draw.line(surf, (0, 0, 0), 
                         (CELL_SIZE//2-2, 2),
                         (CELL_SIZE//2-2, CELL_SIZE-4), 2)
        return surf
        
    def reset_game(self):
        """Initialize a new game"""
        self.first_click = True
        self.game_over = False
        self.victory = False
        self.flags_placed = 0
        
        self.board = [[{'is_bomb': False, 
                       'revealed': False, 
                       'flagged': False, 
                       'adjacent': 0} 
                      for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.grid_rect = pygame.Rect(
            MARGIN,
            TOP_MARGIN,
            GRID_SIZE * CELL_SIZE,
            GRID_SIZE * CELL_SIZE)
        
    def _place_bombs(self, first_click_row, first_click_col):
        """Place bombs randomly while avoiding first click area"""
        bombs_placed = 0
        
        safe_zone = []
        for r in range(max(0, first_click_row-1), min(GRID_SIZE, first_click_row+2)):
            for c in range(max(0, first_click_col-1), min(GRID_SIZE, first_click_col+2)):
                safe_zone.append((r, c))
        
        while bombs_placed < BOMB_COUNT:
            row, col = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            
            if (row, col) not in safe_zone and not self.board[row][col]['is_bomb']:
                self.board[row][col]['is_bomb'] = True
                bombs_placed += 1
                
                for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
                    for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                        self.board[r][c]['adjacent'] += 1
        
        self.first_click = False
    
    def draw(self):
        """Render the game"""
        self.screen.fill(BG_COLOR)
        
        title = self.font.render("MINESWEEPER", True, (50, 50, 50))
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        
        flags_text = self.font.render(f"Flags: {BOMB_COUNT - self.flags_placed}", True, (200, 50, 50))
        self.screen.blit(flags_text, (20, 20))
        
        pygame.draw.rect(self.screen, GRID_COLOR, self.grid_rect)
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.board[row][col]
                rect = pygame.Rect(
                    MARGIN + col * CELL_SIZE,
                    TOP_MARGIN + row * CELL_SIZE,
                    CELL_SIZE - 1,
                    CELL_SIZE - 1)
                
                if cell['revealed'] or self.game_over:
                    pygame.draw.rect(self.screen, REVEALED_CELL, rect)
                    
                    if cell['is_bomb']:
                        self.screen.blit(self.bomb_img, (rect.x+2, rect.y+2))
                    
                    elif cell['adjacent'] > 0:
                        num_text = self.font.render(str(cell['adjacent']), True, TEXT_COLORS[cell['adjacent']])
                        self.screen.blit(num_text, 
                                        (rect.x + CELL_SIZE//2 - num_text.get_width()//2,
                                         rect.y + CELL_SIZE//2 - num_text.get_height()//2))
                else:
                    if cell['flagged']:
                        pygame.draw.rect(self.screen, FLAGGED_CELL, rect)
                    else:
                        pygame.draw.rect(self.screen, HIDDEN_CELL, rect)
                
                if cell['flagged'] and not cell['revealed']:
                    self.screen.blit(self.flag_img, (rect.x+2, rect.y+2))
        
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            message = "VICTORY!" if self.victory else "GAME OVER"
            color = (0, 255, 0) if self.victory else (255, 0, 0)
            text = self.font.render(message, True, color)
            restart_text = self.small_font.render("Press R to restart", True, (255, 255, 255))
            
            self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 10))
    
    def handle_click(self, pos, is_right_click=False):
        """Handle player clicks"""
        if not self.grid_rect.collidepoint(pos) or self.game_over:
            return
            
        col = (pos[0] - MARGIN) // CELL_SIZE
        row = (pos[1] - TOP_MARGIN) // CELL_SIZE
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            cell = self.board[row][col]
            
            if self.first_click:
                self._place_bombs(row, col)
            
            if is_right_click and not cell['revealed']:
                if cell['flagged']:
                    cell['flagged'] = False
                    self.flags_placed -= 1
                elif self.flags_placed < BOMB_COUNT:
                    cell['flagged'] = True
                    self.flags_placed += 1
                return
            
            if not is_right_click and cell['flagged']:
                return
                
            if not cell['revealed'] and not is_right_click:
                self.reveal_cell(row, col)
    
    def reveal_cell(self, row, col):
        """Reveal a cell and potentially adjacent cells"""
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return
        if self.board[row][col]['revealed'] or self.board[row][col]['flagged']:
            return
            
        cell = self.board[row][col]
        cell['revealed'] = True
        
        if cell['is_bomb']:
            self.game_over = True
            self.victory = False
            self.reveal_all_bombs()
            return
        
        if cell['adjacent'] == 0:
            for r in range(max(0, row-1), min(GRID_SIZE, row+2)):
                for c in range(max(0, col-1), min(GRID_SIZE, col+2)):
                    if r != row or c != col:
                        self.reveal_cell(r, c)
                        
        self.check_victory()
    
    def reveal_all_bombs(self):
        """Reveal all bombs when game is lost"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col]['is_bomb']:
                    self.board[row][col]['revealed'] = True
    
    def check_victory(self):
        """Check if player has won (all safe cells revealed)"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.board[row][col]
                if not cell['is_bomb'] and not cell['revealed']:
                    return
        self.game_over = True
        self.victory = True
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.handle_click(event.pos)
                    elif event.button == 3:  
                        self.handle_click(event.pos, True)
                elif event.type == KEYDOWN:
                    if event.key == K_r: 
                        self.reset_game()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()
