import copy 
class GameState :
    def __init__ (self ):
        self .turn ="white"
        from backend .chess_runner import color 
        self .player_color =color 
        self .board =self .create_board ()
        self .move_history =[]
        self .en_passant =None 
        self .castling_rights ={"wK":True ,"wQ":True ,"bK":True ,"bQ":True }
        self .position_history =[self .get_board_string ()]

    def create_board (self ):
        return [
        ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        ["bP"]*8 ,
        ["--"]*8 ,
        ["--"]*8 ,
        ["--"]*8 ,
        ["--"]*8 ,
        ["wP"]*8 ,
        ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]

    def move_piece (self ,start ,end ,promo ="Q",is_simulation =False ):
        if not is_simulation :
            if end not in self .get_legal_moves (start ):
                return False 

        sr ,sc =start 
        er ,ec =end 
        piece =self .board [sr ][sc ]

        if piece [1 ]=="P"and self .en_passant ==(er ,ec ):
            self .board [sr ][ec ]="--"

        self .board [er ][ec ]=piece 
        self .board [sr ][sc ]="--"

        if piece [1 ]=="P"and abs (sr -er )==2 :
            self .en_passant =((sr +er )//2 ,sc )
        else :
            self .en_passant =None 

        if piece =="wK":
            self .castling_rights ["wK"]=False 
            self .castling_rights ["wQ"]=False 
        if piece =="bK":
            self .castling_rights ["bK"]=False 
            self .castling_rights ["bQ"]=False 
        if piece =="wR":
            if sc ==0 :self .castling_rights ["wQ"]=False 
            if sc ==7 :self .castling_rights ["wK"]=False 
        if piece =="bR":
            if sc ==0 :self .castling_rights ["bQ"]=False 
            if sc ==7 :self .castling_rights ["bK"]=False 

        if piece [1 ]=="K"and abs (sc -ec )==2 :
            if ec ==6 :
                self .board [er ][5 ]=self .board [er ][7 ]
                self .board [er ][7 ]="--"
            if ec ==2 :
                self .board [er ][3 ]=self .board [er ][0 ]
                self .board [er ][0 ]="--"

        if piece [1 ]=="P"and er in (0 ,7 ):
            self .board [er ][ec ]=piece [0 ]+promo 

        self .turn ="black"if self .turn =="white"else "white"
        self .move_history .append ((start ,end ))

        if not is_simulation :
            self .position_history .append (self .get_board_string ())

        return True 

    def get_legal_moves (self ,pos ):
        moves =self .get_pseudo_moves (pos )
        legal =[]
        for m in moves :
            copy_board =self .copy_state ()
            copy_board .move_piece (pos ,m ,is_simulation =True )
            if not copy_board .king_in_check (self .turn ):
                legal .append (m )
        return legal 

    def king_in_check (self ,color ):
        king =color [0 ]+"K"
        for r in range (8 ):
            for c in range (8 ):
                if self .board [r ][c ]==king :
                    return self .square_under_attack (r ,c ,color )
        return False 

    def square_under_attack (self ,r ,c ,color ):
        opponent ="black"if color =="white"else "white"
        original_turn =self .turn 
        self .turn =opponent 

        under_attack =False 
        for row in range (8 ):
            for col in range (8 ):
                piece =self .board [row ][col ]
                if piece !="--"and piece [0 ]==opponent [0 ]:
                    if (r ,c )in self .get_pseudo_moves ((row ,col )):
                        under_attack =True 
                        break 
            if under_attack :
                break 

        self .turn =original_turn 
        return under_attack 

    def get_pseudo_moves (self ,pos ):
        r ,c =pos 
        piece =self .board [r ][c ]
        if piece =="--"or piece [0 ]!=self .turn [0 ]:
            return []
        if piece [1 ]=="P":return self .pawn_moves (r ,c )
        if piece [1 ]=="R":return self .rook_moves (r ,c )
        if piece [1 ]=="N":return self .knight_moves (r ,c )
        if piece [1 ]=="B":return self .bishop_moves (r ,c )
        if piece [1 ]=="Q":return self .rook_moves (r ,c )+self .bishop_moves (r ,c )
        if piece [1 ]=="K":return self .king_moves (r ,c )
        return []

    def pawn_moves (self ,r ,c ):
        moves =[]
        dir =-1 if self .turn =="white"else 1 
        start =6 if self .turn =="white"else 1 
        if 0 <=r +dir <8 and self .board [r +dir ][c ]=="--":
            moves .append ((r +dir ,c ))
            if r ==start and self .board [r +2 *dir ][c ]=="--":
                moves .append ((r +2 *dir ,c ))
        for dc in [-1 ,1 ]:
            if 0 <=c +dc <8 and 0 <=r +dir <8 :
                target =self .board [r +dir ][c +dc ]
                if target !="--"and target [0 ]!=self .turn [0 ]:
                    moves .append ((r +dir ,c +dc ))
                if self .en_passant ==(r +dir ,c +dc ):
                    moves .append ((r +dir ,c +dc ))
        return moves 

    def rook_moves (self ,r ,c ):
        return self .slide_moves (r ,c ,[(-1 ,0 ),(1 ,0 ),(0 ,-1 ),(0 ,1 )])

    def bishop_moves (self ,r ,c ):
        return self .slide_moves (r ,c ,[(1 ,1 ),(1 ,-1 ),(-1 ,1 ),(-1 ,-1 )])

    def knight_moves (self ,r ,c ):
        moves =[]
        for d in [(2 ,1 ),(2 ,-1 ),(-2 ,1 ),(-2 ,-1 ),(1 ,2 ),(1 ,-2 ),(-1 ,2 ),(-1 ,-2 )]:
            nr ,nc =r +d [0 ],c +d [1 ]
            if 0 <=nr <8 and 0 <=nc <8 :
                if self .board [nr ][nc ]=="--"or self .board [nr ][nc ][0 ]!=self .turn [0 ]:
                    moves .append ((nr ,nc ))
        return moves 

    def king_moves (self ,r ,c ):
        moves =[]
        for d in [(1 ,1 ),(1 ,-1 ),(-1 ,1 ),(-1 ,-1 ),(1 ,0 ),(-1 ,0 ),(0 ,1 ),(0 ,-1 )]:
            nr ,nc =r +d [0 ],c +d [1 ]
            if 0 <=nr <8 and 0 <=nc <8 :
                if self .board [nr ][nc ]=="--"or self .board [nr ][nc ][0 ]!=self .turn [0 ]:
                    moves .append ((nr ,nc ))
        if self .turn =="white"and r ==7 :
            if self .castling_rights ["wK"]and self .board [7 ][5 ]=="--"and self .board [7 ][6 ]=="--":
                moves .append ((7 ,6 ))
            if self .castling_rights ["wQ"]and self .board [7 ][1 ]=="--"and self .board [7 ][2 ]=="--"and self .board [7 ][3 ]=="--":
                moves .append ((7 ,2 ))
        if self .turn =="black"and r ==0 :
            if self .castling_rights ["bK"]and self .board [0 ][5 ]=="--"and self .board [0 ][6 ]=="--":
                moves .append ((0 ,6 ))
            if self .castling_rights ["bQ"]and self .board [0 ][1 ]=="--"and self .board [0 ][2 ]=="--"and self .board [0 ][3 ]=="--":
                moves .append ((0 ,2 ))
        return moves 

    def slide_moves (self ,r ,c ,directions ):
        moves =[]
        for d in directions :
            for i in range (1 ,8 ):
                nr ,nc =r +d [0 ]*i ,c +d [1 ]*i 
                if 0 <=nr <8 and 0 <=nc <8 :
                    if self .board [nr ][nc ]=="--":
                        moves .append ((nr ,nc ))
                    elif self .board [nr ][nc ][0 ]!=self .turn [0 ]:
                        moves .append ((nr ,nc ))
                        break 
                    else :
                        break 
                else :
                        break 
        return moves 

    def checkmate (self ):
        if not self .king_in_check (self .turn ):
            return False 
        for r in range (8 ):
            for c in range (8 ):
                if self .board [r ][c ]!="--"and self .board [r ][c ][0 ]==self .turn [0 ]:
                    if self .get_legal_moves ((r ,c )):
                        return False 
        return True 

    def stalemate (self ):
        if self .king_in_check (self .turn ):
            return False 
        for r in range (8 ):
            for c in range (8 ):
                if self .board [r ][c ]!="--"and self .board [r ][c ][0 ]==self .turn [0 ]:
                    if self .get_legal_moves ((r ,c )):
                        return False 
        return True 

    def get_board_string (self ):
        return " ".join (self .get_fen ().split (" ")[:4 ])

    def threefold_repetition (self ):
        return self .position_history .count (self .get_board_string ())>=3 

    def copy_state (self ):
        return copy .deepcopy (self )

    def get_fen (self ):
        fen =""
        for row in self .board :
            empty =0 
            for piece in row :
                if piece =="--":
                    empty +=1 
                else :
                    if empty :
                        fen +=str (empty )
                        empty =0 
                    char =piece [1 ]if piece [0 ]=="w"else piece [1 ].lower ()
                    fen +=char 
            if empty :
                fen +=str (empty )
            fen +="/"
        fen =fen [:-1 ]
        turn ="w"if self .turn =="white"else "b"
        cast =""
        if self .castling_rights ["wK"]:cast +="K"
        if self .castling_rights ["wQ"]:cast +="Q"
        if self .castling_rights ["bK"]:cast +="k"
        if self .castling_rights ["bQ"]:cast +="q"
        if cast =="":cast ="-"
        ep ="-"
        if self .en_passant :
            files ="abcdefgh"
            ep =files [self .en_passant [1 ]]+str (8 -self .en_passant [0 ])
        return f"{fen } {turn } {cast } {ep } 0 1"