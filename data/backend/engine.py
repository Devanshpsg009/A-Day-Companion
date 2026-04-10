import chess 
import chess .engine 
import random 

class ChessEngine :
    def __init__ (self ,executable_path ,level ="1500"):
        self .engine =chess .engine .SimpleEngine .popen_uci (executable_path )
        self .set_level (level )

    def set_level (self ,level ):
        elo_map ={
        "500":{"skill":0 ,"depth":1 ,"time":0.05 ,"random":0.70 },
        "800":{"skill":0 ,"depth":1 ,"time":0.05 ,"random":0.50 },
        "1000":{"skill":1 ,"depth":2 ,"time":0.1 ,"random":0.40 },
        "1200":{"skill":3 ,"depth":3 ,"time":0.2 ,"random":0.30 },
        "1500":{"skill":8 ,"depth":5 ,"time":0.5 ,"random":0.20 },
        "1800":{"skill":11 ,"depth":7 ,"time":1.0 ,"random":0.10 },
        "2000":{"skill":14 ,"depth":10 ,"time":1.5 ,"random":0.0 },
        "2200":{"skill":17 ,"depth":12 ,"time":2.0 ,"random":0.0 },
        "2500":{"skill":20 ,"depth":15 ,"time":2.5 ,"random":0.0 },
        "2800":{"skill":20 ,"depth":18 ,"time":5.0 ,"random":0.0 },
        "3000":{"skill":20 ,"depth":22 ,"time":7.0 ,"random":0.0 },
        "Maximum":{"skill":20 ,"depth":None ,"time":8.0 ,"random":0.0 }
        }

        config =elo_map .get (str (level ),elo_map ["1500"])

        self .engine .configure ({
        "Skill Level":config ["skill"],
        "Threads":1 ,
        "Hash":64 
        })

        self .time_limit =config ["time"]
        self .depth =config ["depth"]
        self .random_chance =config ["random"]

    def get_best_move (self ,fen ):
        board =chess .Board (fen )

        if self .random_chance >0 and random .random ()<self .random_chance :
            move =random .choice (list (board .legal_moves ))
        else :
            if self .depth :
                limit =chess .engine .Limit (time =self .time_limit ,depth =self .depth )
            else :
                limit =chess .engine .Limit (time =self .time_limit )

            result =self .engine .play (board ,limit )
            move =result .move 

        start_row =7 -(move .from_square //8 )
        start_col =move .from_square %8 
        end_row =7 -(move .to_square //8 )
        end_col =move .to_square %8 

        return (start_row ,start_col ),(end_row ,end_col )

    def quit (self ):
        try :
            self .engine .quit ()
        except :
            pass 