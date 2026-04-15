
import pygame
import os
from backend.logic import GameState
from backend.engine import ChessEngine
from sys import exit

BASE_DIR =os.path.dirname (os.path.dirname (os.path.abspath (__file__ )))
ASSETS_DIR =os.path.join (BASE_DIR ,"assets")

class ChessGame :
    def __init__ (self ,width ,height ,title ,fps ,engine_path ,level ="1500"):
        self.game_engine =GameState ()
        self.ai =ChessEngine (engine_path ,level )if engine_path else None
        pygame.init ()
        self.width =width
        self.height =height
        self.square_size =width //8

        self.fps =fps
        self.screen =pygame.display.set_mode ((self.width ,self.height ))
        pygame.display.set_caption (title )
        self.clock =pygame.time.Clock ()
        self.light_color =(240 ,217 ,181 )
        self.dark_color =(139 ,69 ,19 )
        self.pieces =self.load_pieces ()
        self.textf =pygame.font.Font (None ,30 )
        self.big_font =pygame.font.Font (None ,80 )
        self.selected_square =()
        self.player_clicks =[]
        self.promotion_pending =None
        self.game_over =False
        try :
            self.move_sound =pygame.mixer.Sound (os.path.join (ASSETS_DIR ,"move.wav"))
        except :
            self.move_sound =None
        try :
            self.capture_sound =pygame.mixer.Sound (os.path.join (ASSETS_DIR ,"capture.wav"))
        except :
            self.capture_sound =None

    def load_pieces (self ):
        piece_paths ={
        "P_w":os.path.join (ASSETS_DIR ,"Chess_plt60.png"),"P_b":os.path.join (ASSETS_DIR ,"Chess_pdt60.png"),
        "B_w":os.path.join (ASSETS_DIR ,"Chess_blt60.png"),"B_b":os.path.join (ASSETS_DIR ,"Chess_bdt60.png"),
        "N_w":os.path.join (ASSETS_DIR ,"Chess_nlt60.png"),"N_b":os.path.join (ASSETS_DIR ,"Chess_ndt60.png"),
        "R_w":os.path.join (ASSETS_DIR ,"Chess_rlt60.png"),"R_b":os.path.join (ASSETS_DIR ,"Chess_rdt60.png"),

        "Q_w":os.path.join (ASSETS_DIR ,"Chess_qlt60.png"),"Q_b":os.path.join (ASSETS_DIR ,"Chess_qdt60.png"),
        "K_w":os.path.join (ASSETS_DIR ,"Chess_klt60.png"),"K_b":os.path.join (ASSETS_DIR ,"Chess_kdt60.png")
        }
        loaded ={}
        for name ,path in piece_paths.items ():
            image =pygame.image.load (path ).convert_alpha ()
            loaded [name ]=pygame.transform.smoothscale (image ,(90 ,90 ))
        return loaded

    def draw_board (self ):
        self.choice =self.game_engine.player_color
        for row in range (8 ):
            for col in range (8 ):
                color =self.light_color if (row +col )%2 ==0 else self.dark_color

                rect =(col *self.square_size ,row *self.square_size ,self.square_size ,self.square_size )
                pygame.draw.rect (self.screen ,color ,rect )

    def draw_highlights (self ):
        if self.selected_square and not self.game_over :
            r ,c =self.selected_square
            render_r ,render_c =(r ,c )if self.choice =="white"else (7 -r ,7 -c )

            s =pygame.Surface ((self.square_size ,self.square_size ))
            s.set_alpha (100 )
            s.fill ((0 ,150 ,0 ))
            self.screen.blit (s ,(render_c *self.square_size ,render_r *self.square_size ))
            valid_moves =self.game_engine.get_legal_moves ((r ,c ))
            for move in valid_moves :
                move_r ,move_c =(move [0 ],move [1 ])if self.choice =="white"else (7 -move [0 ],7 -move [1 ])
                pygame.draw.circle (self.screen ,(0 ,0 ,255 ),
                (move_c *self.square_size +50 ,move_r *self.square_size +50 ),15 )

    def draw_pieces (self ,exclude_square =None ):
        for row in range (8 ):
            for col in range (8 ):

                if (row ,col )==exclude_square :
                    continue
                piece =self.game_engine.board [row ][col ]
                if piece !="--":
                    key =f"{piece [1 ]}_{piece [0 ]}"
                    if key in self.pieces :
                        r ,c =(row ,col )if self.choice =="white"else (7 -row ,7 -col )
                        self.screen.blit (self.pieces [key ],(c *self.square_size +5 ,r *self.square_size +5 ))

    def animate_move (self ,start ,end ):
        r1 ,c1 =start

        r2 ,c2 =end

        if self.choice =="black":
            render_r1 ,render_c1 =7 -r1 ,7 -c1
            render_r2 ,render_c2 =7 -r2 ,7 -c2
        else :
            render_r1 ,render_c1 =r1 ,c1
            render_r2 ,render_c2 =r2 ,c2

        dr =render_r2 -render_r1
        dc =render_c2 -render_c1
        frames_per_square =3
        frame_count =max (1 ,(abs (dr )+abs (dc ))*frames_per_square )

        piece =self.game_engine.board [r1 ][c1 ]
        if piece =="--":
            return
        piece_image =self.pieces [f"{piece [1 ]}_{piece [0 ]}"]

        for frame in range (frame_count +1 ):
            r =render_r1 +dr *frame /frame_count
            c =render_c1 +dc *frame /frame_count
            self.draw_board ()
            self.draw_highlights ()
            self.draw_pieces (exclude_square =start )
            self.screen.blit (piece_image ,(c *self.square_size +5 ,r *self.square_size +5 ))
            pygame.display.update ()
            self.clock.tick (self.fps )

    def draw_game_over (self ):

        overlay =pygame.Surface ((self.width ,self.height ))
        overlay.set_alpha (150 )
        overlay.fill ((0 ,0 ,0 ))
        self.screen.blit (overlay ,(0 ,0 ))

        text_surface =self.big_font.render ("Game Over",True ,(255 ,0 ,0 ))
        text_rect =text_surface.get_rect (center =(self.width //2 ,self.height //2 -30 ))
        self.screen.blit (text_surface ,text_rect )

        sub_surface =self.textf.render ("Click anywhere to restart",True ,(255 ,255 ,255 ))
        sub_rect =sub_surface.get_rect (center =(self.width //2 ,self.height //2 +30 ))
        self.screen.blit (sub_surface ,sub_rect )


    def run (self ):
        while True :
            for event in pygame.event.get ():
                if event.type ==pygame.QUIT :
                    if self.ai :
                        self.ai.quit ()
                    pygame.quit ()

                elif event.type ==pygame.KEYDOWN :
                    if event.key ==pygame.K_r and not self.game_over :
                        self.game_over =True

                elif event.type ==pygame.MOUSEBUTTONDOWN :
                    if self.game_over :
                        self.game_engine =GameState ()
                        self.game_over =False
                        self.selected_square =()
                        self.player_clicks =[]
                        continue
                    if self.game_engine.turn ==self.game_engine.player_color :
                        pos =pygame.mouse.get_pos ()
                        col ,row =pos [0 ]//self.square_size ,pos [1 ]//self.square_size
                        if self.game_engine.player_color =="black":
                            row ,col =7 -row ,7 -col
                        if self.selected_square ==(row ,col ):
                            self.selected_square =()
                            self.player_clicks =[]
                        else :
                            self.selected_square =(row ,col )
                            self.player_clicks.append (self.selected_square )

                        if len (self.player_clicks )==2 :
                            start ,end =self.player_clicks
                            if end in self.game_engine.get_legal_moves (start ):
                                target_piece =self.game_engine.board [end [0 ]][end [1 ]]
                                moving_piece =self.game_engine.board [start [0 ]][start [1 ]]
                                is_en_passant =moving_piece [1 ]=="P"and start [1 ]!=end [1 ]and target_piece =="--"
                                is_capture =target_piece !="--"or is_en_passant

                                self.animate_move (start ,end )
                                self.game_engine.move_piece (start ,end )

                                if is_capture and self.capture_sound :
                                    self.capture_sound.play ()
                                elif self.move_sound :
                                    self.move_sound.play ()

                                if self.game_engine.checkmate ()or self.game_engine.stalemate ()or self.game_engine.threefold_repetition ():
                                    self.game_over =True

                            self.selected_square =()
                            self.player_clicks =[]


            if not self.game_over and self.ai and self.game_engine.turn !=self.game_engine.player_color :
                self.draw_board ()
                self.draw_pieces ()
                pygame.display.update ()
                fen =self.game_engine.get_fen ()
                s ,e =self.ai.get_best_move (fen )

                if s and e :
                    target_piece_ai =self.game_engine.board [e [0 ]][e [1 ]]
                    moving_piece_ai =self.game_engine.board [s [0 ]][s [1 ]]
                    is_en_passant_ai =moving_piece_ai [1 ]=="P"and s [1 ]!=e [1 ]and target_piece_ai =="--"
                    is_capture_ai =target_piece_ai !="--"or is_en_passant_ai

                    self.animate_move (s ,e )
                    self.game_engine.move_piece (s ,e )

                    if is_capture_ai and self.capture_sound :
                        self.capture_sound.play ()
                    elif self.move_sound :
                        self.move_sound.play ()

                    if self.game_engine.checkmate ()or self.game_engine.stalemate ()or self.game_engine.threefold_repetition ():
                        self.game_over =True

            self.draw_board ()
            self.draw_highlights ()
            self.draw_pieces ()

            if self.game_over :
                self.draw_game_over ()

            pygame.display.update ()
            self.clock.tick (self.fps )