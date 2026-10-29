import chess as ch
import pygame
import os
import math


class Chess_GUI_wrapper:
    """Connect a python-chess board to a Pygame window and mouse controls."""

    def __init__(self, square_size, board_size, player_first=False):
        # Save the board layout and which side the human player controls.
        self.player_first = player_first
        self.square_size = square_size
        self.board_size = board_size
       

        # The window is a square made from board_size rows and columns.
        self.screen_size = (self.square_size*self.board_size, self.square_size*self.board_size)
        # RGB colors used to draw alternating board squares.
        self.dark = (68, 32, 10)
        self.light = (240, 209, 145)
        

        # Initialize Pygame and create the display and frame-rate clock.
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock() 
        self.running = True
        self.framerate = 60

        # Start from the standard chess position.
        self.board_state = ch.Board()

        # Load each PNG and associate its image with a python-chess piece symbol.
        # The filenames are expected to follow names such as "Light_p.png".
        self.piece_name_dict = self.filename_to_chesssymb({
        self.load(os.path.join('Chess_icons', file), file):os.path.splitext(file)[0]
        for file in os.listdir('Chess_icons') if file.endswith((".png"))
            })
        # Resize the loaded piece images so each one fits a board square.
        self.piece_name_dict = self.scale_to_board(self.piece_name_dict)

        # None means that the mouse is not currently holding a selected square.
        self.selected_square = None

        # Holds a move intended for the computer side; None means no move is queued.
        self.computer_move_var = None
        



    def board_turn_adjuster(self, file, rank):
         """Convert between screen coordinates and board coordinates.

         When player_first is true, reverse the rank so the board is viewed
         from the opposite side. Files are not reversed.
         """
         if self.player_first:
              # Rank 0 maps to 7, rank 1 to 6, and so on.
              return file, 7-rank
         else: 
              # Keep the coordinates unchanged for the normal orientation.
              return file, rank

    def fit(self, val, maxv, minv):
        """Clamp val so it stays between minv and maxv."""
        
        # Apply the lower bound first and then the upper bound.
        val = max(minv, val)
        val = min(maxv, val)
        return val

    def load(self, image_dir, filename):
        """Load an image with transparency from image_dir.

        filename is currently unused; image_dir contains the actual path.
        """
        # convert_alpha preserves transparent pixels and uses the display format.
        loaded = pygame.image.load(image_dir).convert_alpha()

        return loaded

    

    def filename_to_chesssymb(self, file_dict):
        """Translate piece image filenames into python-chess symbols.

        For example, "Light_p" becomes "P" and "Dark_p" becomes "p".
        The input dictionary maps image objects to their filename stems.
        """
        
        # Extract the filename stems from the input dictionary.
        filenames = list(file_dict.values())

        new_ref = []

        # Uppercase letters represent White pieces; lowercase letters represent Black.
        for name in filenames:
            if 'Light_' in name:
                name = name.replace('Light_', '')
                name = name.upper()
                new_ref.append(name)
            if 'Dark_' in name:
                        name = name.replace('Dark_', '')
                        name = name.lower()
                        new_ref.append(name)

        # Pair each converted symbol with the corresponding image key.
        new_dict = {ref:img for ref, img in zip(new_ref, file_dict)}
        print(new_ref)

        return new_dict


    def scale_to_board(self, image_dict):
        """Return a symbol-to-image dictionary with images sized to one square."""
        # Transform each loaded image in place in this temporary list.
        images = list(image_dict.values())
        for i  in range(len(images)):
            images[i] = pygame.transform.scale(images[i], (self.square_size*1, self.square_size*1))

        # Rebuild the dictionary using the original symbols and scaled images.
        image_dict = {ref:img for ref, img in zip(image_dict, images)}

        return image_dict

    def push_move_san_not(self, chess_move_obj:ch.Move):
         """Push a move if it is legal; otherwise raise a ValueError."""
         # Note: in python-chess, legal_moves is an iterable property, not a method.
         if chess_move_obj in self.board_state.legal_moves:
              self.board_state.push(chess_move_obj)
         else:
              raise ValueError(f'illegal move submitted: {chess_move_obj}')


    def render_board(self, test=False):
        """Draw the board position, or print square contents when test is True."""

        # i and j are the board file and rank being inspected.
        for i in range(self.board_size):
            for j in range(self.board_size):
                if not test:
                    # Flip only the displayed rank; keep i and j for board lookup.
                    _, j_flipped = self.board_turn_adjuster(i,j)

                    # Draw the square at its screen location using checkerboard colors.
                    pygame.draw.rect(self.screen, (self.light if (i+j_flipped)%2 == 0 else self.dark), (i*self.square_size, j_flipped*self.square_size, self.square_size, self.square_size))

                # Convert board file/rank to python-chess's integer square index.
                square = ch.square(i, j)
                piece = self.board_state.piece_at(square)
                # Empty squares have no piece image to draw.
                if (not piece == None) and (not test) :
                    # Look up the piece image by its symbol and draw it over the square.
                    self.screen.blit(self.piece_name_dict[piece.symbol()],(i*self.square_size, j_flipped*self.square_size))
                if test:
                    # Diagnostic mode: print the square index and its piece (or None).
                    print(f'square: {square}')
                    print(piece)


    def on_click(self, click_event):
         """Return the board square under a left mouse-button press."""
         # Ignore mouse buttons other than the left button.
         if click_event.button == 1:
            # Convert the pixel location into screen column/row coordinates.
            x, y = click_event.pos
            file, rank = math.floor(x/self.square_size),  math.floor(y/self.square_size)
            # Convert from displayed orientation back to board orientation.
            file, rank = self.board_turn_adjuster(file, rank)
            print(f'file: {file}, rank: {rank}')
            # python-chess represents a square as an integer from 0 to 63.
            square = ch.square(file, rank)
            return square

    def on_button_up(self, unclick_event):
         """Try to move the selected piece to the square where the mouse was released."""
         # Do nothing if no source square has been selected.
         if not self.selected_square == None:
            # Convert the release location from pixels to board coordinates.
            x, y = unclick_event.pos
            new_file, new_rank = math.floor(x/self.square_size),  math.floor(y/self.square_size)
            # Match the coordinate orientation used when the piece was selected.
            new_file, new_rank = self.board_turn_adjuster(new_file, new_rank)
            new_square = ch.square(new_file, new_rank)

            print(f'new square is" {new_square}')
            # Build a move from the selected source square to the release square.
            move = ch.Move(self.selected_square, new_square)  
            # Push only legal moves, and only when it is the human player's turn.
            if (move in self.board_state.legal_moves) and ((self.board_state.turn == ch.WHITE) == self.player_first): 
                self.board_state.push(move)
                print('board has been updated')
            else:
                print('move is not valid')
                


    def update_select_piece(self, xy:tuple):
        """Draw the currently selected piece next to the mouse position."""
        # Read the mouse position in pixels and find the selected piece's image.
        x, y = xy
        im_piece = self.piece_name_dict[self.board_state.piece_at(self.selected_square).symbol()]
        # Center the image under the cursor and clamp it to the window bounds.
        self.screen.blit(im_piece, 
                            (self.fit(x-self.square_size*0.5, minv=0, maxv=self.screen_size[0]-self.square_size*0.5), 
                            self.fit(y-self.square_size*0.5, minv=0, maxv=self.screen_size[0]-self.square_size*0.5))
                            )

    def handle_ext_move(self, move):
         """Apply a move received from the external/computer side when appropriate."""
         # The external side is whichever side is not controlled by the human.
         ext_first = not(self.player_first)

         # The board turn is a bool: True means White to move, False means Black.
         if ext_first == (self.board_state.turn == ch.WHITE):
              # Only apply a move that python-chess recognizes as legal.
              if move in self.board_state.legal_moves:
                   self.board_state.push(move)
             
    def tickstep(self, external_move, framerate=60):
        """Process one frame: events, drawing, an optional move, and timing."""
        # Retrieve queued Pygame events once and stop the loop if the window closes.
        events = pygame.event.get()
        for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

        # Draw the current board position before handling this frame's interaction.
        self.render_board()
        
        # Handle mouse input events from this frame.
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Remember which square was pressed.
                self.selected_square = self.on_click(click_event=event)

            if event.type == pygame.MOUSEBUTTONUP:
                 # Attempt the move, then stop tracking the selected square.
                 self.on_button_up(unclick_event=event)
                 self.selected_square = None

        # While the mouse is held, redraw the selected piece at the cursor.
        if self.selected_square != None:
            if self.board_state.piece_at(self.selected_square) != None:
                self.update_select_piece(pygame.mouse.get_pos())
            

        # Apply a move supplied by the caller, if one is available.
        if external_move != None:
            self.handle_ext_move(external_move)

        # Present the completed frame and limit the loop to the requested rate.
        pygame.display.flip()
        self.clock.tick(framerate)

    def _demo_computer_move(self, tick):
        """Choose a fixed demonstration move based on the configured side and tick."""
        if self.player_first:
                # Intended to play e5 as Black after White has moved.
                if self.board_state.turn == ch.BLACK:
                    self.computer_move_var = self.board_state.parse_san('e5')
                    
                    
        else:
            # After one second at the configured frame rate, choose e4.
            if tick == self.framerate:
                self.computer_move_var = self.board_state.parse_san('e4')


    def run(self):
         """Run the main event loop until the Pygame window is closed."""
         # Count frames so the demonstration move can be triggered after a delay.
         tick = 0
         # This local is currently unused; computer_move_var stores the queued move.
         move = None
         # This local is currently unused; _demo_computer_move no longer needs it.
         try_move = True
         while self.running:
            tick += 1
            # Update the demonstration computer's move for this frame.
            self._demo_computer_move(tick)

            # Process events, render, apply the queued move, and cap the frame rate.
            self.tickstep(self.computer_move_var, framerate=self.framerate) 

    def computer_move(self, move):
        """Check whether it is the computer's turn and whether move is legal."""
        # The computer controls the side opposite the human player's side.
        computer_first = not self.player_first
        # Check that the board's side to move matches the computer's side.
        if  computer_first == (self.board_state.turn):
            # Queue a legal move for tickstep to apply.
            if move in self.board_state.legal_moves:
                   self.computer_move_var = move
            else:
                print(f'move {move} is not legal on the board')
        else:
            print(f'not computer\'s turn yet')

                                  




def main():
     """Create the chess GUI and start the event loop."""
     # Create a 100-pixel-square, 8-by-8 board; player_first is truthy (1).
     chess_board = Chess_GUI_wrapper(square_size=100, board_size=8, player_first=0)
     chess_board.run()

if __name__ == '__main__':
    # Run main only when this file is executed directly, not when imported.
    main()
     




