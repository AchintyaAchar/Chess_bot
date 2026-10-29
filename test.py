import pygame
import chess as ch
import os
import math

SQUARE_SIZE = 100
BOARD_SIZE = 8
SCREEN_SIZE = (SQUARE_SIZE*BOARD_SIZE, SQUARE_SIZE*BOARD_SIZE)
HUMAN_PLAYER_COLOUR = ch.BLACK

dark = (68, 32, 10)
light = (240, 209, 145)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock() 
running = True

board_state = ch.Board()


def fit(val, maxv, minv):
    val = max(minv, val)
    val = min(maxv, val)
    return val

#setting up the piece sprites:

def load(image_dir, filename):

    loaded = pygame.image.load(image_dir).convert_alpha()

    return loaded

image_filetopiece_dict = {
    load(os.path.join('Chess_icons', file), file):os.path.splitext(file)[0]
    for file in os.listdir('Chess_icons') if file.endswith((".png"))

}



def filename_to_chesssymb(file_dict):

    filenames = list(file_dict.values())

    new_ref = []

    for name in filenames:
        if 'Light_' in name:
            name = name.replace('Light_', '')
            name = name.upper()
            new_ref.append(name)
        if 'Dark_' in name:
                    name = name.replace('Dark_', '')
                    name = name.lower()
                    new_ref.append(name)

    new_dict = {ref:img for ref, img in zip(new_ref, file_dict)}
    print(new_ref)

    return new_dict


piece_name_dict = filename_to_chesssymb(image_filetopiece_dict)


def scale_to_board(image_dict):
    images = list(image_dict.values())
    for i  in range(len(images)):
        images[i] = pygame.transform.scale(images[i], (SQUARE_SIZE*1, SQUARE_SIZE*1))

    image_dict = {ref:img for ref, img in zip(image_dict, images)}

    return image_dict

piece_name_dict = scale_to_board(piece_name_dict)



def render_board(screen=None, clock=None, board=None, test=False,):

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if not test:
                if (i+j)%2 == 0:
                    pygame.draw.rect(screen, light, (i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                    

                else:
                    pygame.draw.rect(screen, dark, (i*SQUARE_SIZE, j*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            square = ch.square(i, j)
            
            piece = board.piece_at(square)
            if (not piece == None) and (not test) :
                screen.blit(piece_name_dict[piece.symbol()],(i*SQUARE_SIZE, j*SQUARE_SIZE))
            if test:
                print(f'square: {square}')
                print(piece)
            
                
                
            
    
def handle_click_on_piece(piece, square, im_piece=None, mouse_pos=None, event=None, screen=None, board=None):

    if not mouse_pos == None:
        x, y = mouse_pos
    if not event == None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                file, rank = math.floor(x/SQUARE_SIZE),  math.floor(y/SQUARE_SIZE)
                print(f'file: {file}, rank: {rank}')
                square = ch.square(file, rank)
                piece = board.piece_at(square)
                return piece, square
            
        elif event.type == pygame.MOUSEBUTTONUP:
                print('entered the event action for unclick')
                if not piece == None:
                    
                    new_file, new_rank = math.floor(x/SQUARE_SIZE),  math.floor(y/SQUARE_SIZE)
                    new_square = ch.square(new_file, new_rank)
                    print(f'new square is" {new_square}')
                    move = ch.Move(square, new_square)  
                    if move in board.legal_moves: 
                        board.push(move)
                        print('board has been updated')
                    else:
                        print('move is not valid')
                        pass


    else:
        if not im_piece == None:
            screen.blit(im_piece, 
                                (fit(x-SQUARE_SIZE*0.5, minv=0, maxv=SCREEN_SIZE[0]-SQUARE_SIZE*0.5), 
                                fit(y-SQUARE_SIZE*0.5, minv=0, maxv=SCREEN_SIZE[0]-SQUARE_SIZE*0.5))
                                )
            print('ran blit for pending piece')
                
            
piece = None
square = None

game_tick = 0
while running:
    game_tick += 1
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    render_board(screen, clock, board_state)
        

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            piece, square = handle_click_on_piece(piece=piece, square=square, event=event, screen=screen, board=board_state, mouse_pos=pygame.mouse.get_pos())
            try:
                im_piece = piece_name_dict[piece.symbol()]
            except:
                 pass

    
        

        if event.type == pygame.MOUSEBUTTONUP:
                      handle_click_on_piece(piece=piece, square=square, event=event, screen=screen, board=board_state, mouse_pos=pygame.mouse.get_pos())
                      piece = None
                      square = None
                      im_piece = None

    if not piece == None:
                handle_click_on_piece(piece=piece, square=square, screen=screen, board=board_state, mouse_pos=pygame.mouse.get_pos(), im_piece=im_piece)
    
    if game_tick == 60:
         print('moving piece')
         try:
              move_san = board_state.parse_san('e4')
              board_state.push(move_san)
         except ValueError:
              print('invalid move')
    pygame.display.flip()

    clock.tick(60)




