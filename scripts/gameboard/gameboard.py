from email import message
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import os
import threading
import queue

from scripts.gameboard.gameboardapi import gameboardapi
from . import *

g_icon = Image.open(os.path.dirname(__file__) + "/resources/img/chess-shitty-icons.png").convert("RGBA")
IconMap1 = {
    "king": g_icon.crop([0,100,90,220]),
    "queen": g_icon.crop([160,100,280,220]),
    "rook": g_icon.crop([350,105,450,225]),
    "bishop": g_icon.crop([525,100,625,220]),
    "knight": g_icon.crop([705,105,805,225]),
    "pawn": g_icon.crop([880,105,980,225])
}
IconMap2 = {
    "king": g_icon.crop([0,250,90,370]),
    "queen": g_icon.crop([160,250,280,370]),
    "rook": g_icon.crop([350,255,450,375]),
    "bishop": g_icon.crop([525,250,625,370]),
    "knight": g_icon.crop([705,255,805,375]),
    "pawn": g_icon.crop([880,255,980,375])
}

class GameMenu:
    """
    It is the entry class for the application.
    """
    def __init__(self, sc_api = None, w = 400, h = 325) -> None:
        self.__gameapi = sc_api
        
        self.__window = tk.Tk()
        self.__window.title("Chess Board")
        self.__window.geometry(str(w)+"x"+str(h))

        tk.Label(master=self.__window, text="Chess On Blockchain", font="Helvetica 12 bold").pack(pady=10)

        welcommsg = "\n".join(["You are logged in as:", str(sc_api.Address())])
        tk.Label(master=self.__window, text=welcommsg, font='Helvetica 10').pack(pady=15)

        tk.Label(master=self.__window, text="Bet (wei): ", anchor="w").pack(fill=tk.X, padx=10)
        self.__bet = tk.Entry(master=self.__window)
        self.__bet.pack(fill=tk.X, padx=10)
        self.__bet.insert(0, "1000000000")

        # create board with single player
        self.__btns = []
        self.__btns.append(tk.Button(master=self.__window, text="New Game - Single Player", command=self.__TK_HandleSinglePlayer))
        self.__btns[-1].pack(fill=tk.X, padx=10, pady=5)
        
        # create board and join as player 1
        self.__btns.append(tk.Button(master=self.__window,  text="New Game - MultiPlayers", command=lambda j=False: self.__TK_HandleMultiPlayers(j)))
        self.__btns[-1].pack(fill=tk.X, padx=10, pady=5)

        # join an existing board
        self.__btns.append(tk.Button(master=self.__window,  text="Join a Game", command=lambda j=True: self.__TK_HandleMultiPlayers(j)))
        self.__btns[-1].pack(fill=tk.X, padx=10, pady=(20,5))
        tk.Label(master=self.__window, text="Contract Address: ", anchor="w").pack(fill=tk.X, padx=10)
        self.__contract_address = tk.Entry(master=self.__window)
        self.__contract_address.pack(fill=tk.X, padx=10)
    
    def mainLoop(self):
        """Start showing UI"""
        self.__window.mainloop()

    def __TK_HandleSinglePlayer(self):
        if self.__gameapi is not None:
            for btn in self.__btns: btn["state"]="disabled"
            try:
                resp = self.__gameapi.NewGame()
                messagebox.showinfo("Success", "Gas used for the new game: "+ str(resp["gas_used"]))
            except Exception as e:
                messagebox.showerror("error", str(e))
                for btn in self.__btns: btn["state"]="normal"
                return
            self.__window.destroy()
            game = ChessGame(self.__gameapi)
            game.UpdateRefreshData(True)
            game.mainLoop()

    def __TK_HandleMultiPlayers(self, isjoin = False):
        if self.__gameapi is not None:
            for btn in self.__btns: btn["state"]="disabled"
            
            try:
                if isjoin:
                    resp = self.__gameapi.JoinGame(self.__contract_address.get(), int(self.__bet.get()))
                else:
                    resp = self.__gameapi.NewGame(int(self.__bet.get()), int(self.__bet.get())) # default bet in wei, 1 gwei = 1e9 wei
                messagebox.showinfo("Success", "Gas used for enterring the game: "+ str(resp["gas_used"]))
            except Exception as e:
                messagebox.showerror("error", str(e))
                for btn in self.__btns: btn["state"]="normal"
                return
            self.__window.destroy()
            game = ChessGame(self.__gameapi)
            game.UpdateRefreshData(True)
            game.mainLoop()
        self.__window.destroy()


class ChessGame:
    """
    application logics for game board UI\n
    The constructor argument takes the api class gameboardapi in order to associate with the board data on the blockchain\n
    Call mainLoop() to start running the application\n
    Call UpdateRefreshData() to refresh data and render the board
    """

    class Selection:
        """
        stateful data structure to the pieces selected by player
        """
        def __init__(self):
            self.Clear()
        
        def Set(self, r, c, gamepiece):
            if self.state == 0: # no selection
                self.gamepiece = gamepiece
                self.state = 1 if self.gamepiece is not None else 0
            elif self.state == 1: # selected a piece 
                self.state = 2
                self.r = r
                self.c = c
            elif self.state == 2 and gamepiece is not None: # clear on selecting same piece
                if self.gamepiece is gamepiece:
                    self.Clear()
                
        def isAtMovingLoc(self, r, c):
            return self.r == r and self.c == c if self.state == 2 else False
        
        def isSelected(self, r, c):
            return self.gamepiece.IsAt(r,c) if self.gamepiece is not None else False

        def Clear(self):
            self.state = 0
            self.r = -1
            self.c = -1
            self.gamepiece = None
    

    def __init__(self, sc_api = None, w = 800, h = 750):
        # interfacing with smart contract
        self.api = sc_api
        # model
        self.__afterapi = False
        self.__afterselect = False
        self.__afterrefresh = False
        self.__lastgasused = None
        self.__refresh_thread = None
        self.__uilock = threading.Lock()
        self.__eventq = queue.Queue()
        self.selection = self.Selection()
        # view
        self.__window = tk.Tk()
        self.__window.title("Chess Board")
        self.__window.geometry(str(w)+"x"+str(h))
        self.__window.rowconfigure(3, minsize=0, weight=1)
        self.__window.columnconfigure(1, minsize=0, weight=1)
        self.__board = tk.Frame(master=self.__window, bg="#555", width=600, height=600)
        self.__board.grid(row=0, column=0, padx=5, pady=10)
        self.__board.grid_propagate(False)
        self.__board.rowconfigure(8)
        self.__board.columnconfigure(8)
        self.__board_rev = True

        rightpanel = tk.Frame(master=self.__window, width=160, height=600)
        rightpanel.grid(row=0, column=1)
        rightpanel.grid_propagate(False)

        self.__panel = tk.Frame(master=rightpanel, bg="#A88", borderwidth=1, relief="solid", width=150, height=520)
        self.__panel.grid(row=0, column=0, padx=2, pady=10)
        self.__panel.grid_propagate(False)

        self.__progbar = ttk.Progressbar(master=self.__window, mode='indeterminate', length=780)
        self.__setProgress(False)
        
        self.__status = tk.LabelFrame(master=self.__window, borderwidth=1, relief="solid", width=780, height=100)
        self.__status.grid(row=2, columnspan=2, padx=5, pady=5)
        self.__status.grid_propagate(False)
        self.__status.rowconfigure(5)
        self.__status.columnconfigure(3)

        tk.Label(master=self.__status, text="Board Address: ", font='Helvetica 10 bold', anchor="w", width=15).grid(row=0, column=0)
        self.__status_board = tk.Entry(master=self.__status, width=50)
        self.__status_board.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.__status_board.insert(0, "0x0000000000000000000000000000000000000000")
        tk.Label(master=self.__status, text="Turn: ", font='Helvetica 10 bold', anchor="w", width=15).grid(row=1, column=0)
        self.__status_turn = tk.Label(master=self.__status, text="Black", anchor="w", width=50)
        self.__status_turn.grid(row=1, column=1)
        tk.Label(master=self.__status, text="Player One (B): ", font='Helvetica 10 bold', anchor="w", width=15).grid(row=2, column=0)
        self.__status_playerone = tk.Label(master=self.__status, text="0x0000000000000000000000000000000000000000", anchor="w", width=50)
        self.__status_playerone.grid(row=2, column=1)
        self.__status_playerone_state = tk.Label(master=self.__status, text="Normal (Bet=10000000000000 wei)", anchor="w", width=35)
        self.__status_playerone_state.grid(row=2, column=2)
        tk.Label(master=self.__status, text="Player Two (W): ", font='Helvetica 10 bold', anchor="w", width=15).grid(row=3, column=0)
        self.__status_playertwo = tk.Label(master=self.__status, text="0x0000000000000000000000000000000000000000", anchor="w", width=50)
        self.__status_playertwo.grid(row=3, column=1)
        self.__status_playertwo_state = tk.Label(master=self.__status, text="Normal (Bet=10000000000 wei)", anchor="w", width=35)
        self.__status_playertwo_state.grid(row=3, column=2)

        self.__btn_submit = tk.Button(master=self.__panel, width=18, bg = "grey", text="Move", command=lambda : self.__TK_HandleSubmit())
        self.__btn_submit.grid(row=0,column=0, padx=(6,0), pady=5)
        #btn.pack(fill=tk.X, side=tk.TOP)
        self.__btn_submit["state"] = 'disabled'

        self.__btn_castling = tk.Button(master=self.__panel, width=18, bg = "grey", text="Castling", command=lambda : self.__TK_HandleSubmit("Castle"))
        self.__btn_castling.grid(row=1,column=0, padx=(6,0), pady=5)
        self.__btn_castling["state"] = 'disabled'

        self.__btn_pm_queen = tk.Button(master=self.__panel, width=18, bg = "grey", text="Promote Queen", command=lambda : self.__TK_HandleSubmit("PromoteToQueen"))
        self.__btn_pm_queen.grid(row=2,column=0, padx=(6,0), pady=5)
        self.__btn_pm_queen["state"] = 'disabled'
        self.__btn_pm_bishop = tk.Button(master=self.__panel, width=18, bg = "grey", text="Promote Bishop", command=lambda : self.__TK_HandleSubmit("PromoteToBishop"))
        self.__btn_pm_bishop.grid(row=3,column=0, padx=(6,0), pady=5)
        self.__btn_pm_bishop["state"] = 'disabled'
        self.__btn_pm_knight = tk.Button(master=self.__panel, width=18, bg = "grey", text="Promote Knight", command=lambda : self.__TK_HandleSubmit("PromoteToKnight"))
        self.__btn_pm_knight.grid(row=4,column=0, padx=(6,0), pady=5)
        self.__btn_pm_knight["state"] = 'disabled'
        self.__btn_pm_rook = tk.Button(master=self.__panel, width=18, bg = "grey", text="Promote Rook", command=lambda : self.__TK_HandleSubmit("PromoteToRook"))
        self.__btn_pm_rook.grid(row=5,column=0, padx=(6,0), pady=5)
        self.__btn_pm_rook["state"] = 'disabled'

        self.__btn_cmd_pass = tk.Button(master=self.__panel, width=18, bg = "grey", text="Pass", command=lambda : self.__TK_HandleSubmit("Pass"))
        self.__btn_cmd_pass.grid(row=6,column=0, padx=(6,0), pady=5)
        self.__btn_cmd_withdraw = tk.Button(master=self.__panel, width=18, bg = "grey", text="Withdraw", command=lambda : self.__TK_HandleSubmit("Withdraw"))
        self.__btn_cmd_withdraw.grid(row=7,column=0, padx=(6,0), pady=5)

        self.__btn__cmd_win = tk.Button(master=self.__panel, width=18, bg = "grey", text="I Won", command=lambda : self.__TK_HandleWin() )
        self.__btn__cmd_win.grid(row=8, column=0, padx=(6,0), pady=5)
        
        self.__lbl_lastgasused = tk.Label(master=rightpanel, bg="white", text="Last gas used:\n--", width=18, font='Helvetica 10 bold')
        self.__lbl_lastgasused.grid(row=1, column=0, pady=10)

    def mainLoop(self):
        self.__window.after(10, self.__After_Handlers)
        self.__window.after(10000, self.__After_Poll)
        self.__window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.__window.mainloop()

    def UpdateRefreshData(self, isui=False):
        """
        Call API to obtain latest data. \n
            isui: True if caller request update the UI by the way \n
         """
        if (self.api is not None):
            my_addr = self.api.Address()
            (boardaddr, boardarr, gamectx) = self.api.UpdatePieces()
            (GP1, GP2) = gameboardapi.ParseBoardPieceInfo(boardarr)
            gamectx = gameboardapi.GameContext(boardaddr, gamectx[0],gamectx[1],gamectx[2],gamectx[3])
            self.__GP1 = GP1
            self.__GP2 = GP2
            self.__CTX = gamectx
            if isui: self.__RenderBoard(my_addr) # explicitly render UI requested from caller

    def __setProgress(self, isloading):
        if isloading:
            self.__progbar.grid(row=1, column=0, columnspan=2, pady=2)
            self.__progbar.start()
        else:
            self.__progbar.grid_forget()
    
    def __setButtonsState(self): 
        if self.selection.state == 2 :
            self.__btn_submit["state"] = 'normal'
            if self.selection.gamepiece is not None and self.selection.gamepiece.PieceType() == "rook":
                self.__btn_castling["state"] = 'normal'
            if self.selection.gamepiece is not None and self.selection.gamepiece.PieceType() == "pawn" \
                and (self.selection.r == 0 or self.selection.r == 7):
                self.__btn_pm_queen["state"] = 'normal'
                self.__btn_pm_bishop["state"] = 'normal'
                self.__btn_pm_knight["state"] = 'normal'
                self.__btn_pm_rook["state"] = 'normal'

        else :
            self.__btn_submit["state"] = 'disabled'
            self.__btn_castling["state"] = 'disabled'
            self.__btn_pm_queen["state"] = 'disabled'
            self.__btn_pm_bishop["state"] = 'disabled'
            self.__btn_pm_knight["state"] = 'disabled'
            self.__btn_pm_rook["state"] = 'disabled'
        pass


    def __RenderBoard(self, player_addr = None):
        # update status board
        self.__status_board.delete(0, tk.END)
        self.__status_board.insert(0, self.__CTX.address)
        self.__status_turn.config(text = self.__CTX.Turn())
        self.__status_playerone.config(text = self.__CTX.player1.address)
        self.__status_playerone_state.config(text = self.__CTX.player1.StateDesc())
        self.__status_playertwo.config(text = self.__CTX.player2.address)
        self.__status_playertwo_state.config(text = self.__CTX.player2.StateDesc())
        if player_addr is not None:
            self.__board_rev = player_addr != self.__CTX.player2.address
            
        if self.__lastgasused is not None:
            self.__lbl_lastgasused.config(text="Last gas used:\n"+str(self.__lastgasused))
        else:
            self.__lbl_lastgasused.config(text="Last gas used:\n--")

        # destroy all widgets from frame and clear frame and frame will be empty
        for widget in self.__board.winfo_children():
            widget.destroy()
        self.__board.pack_forget()
        # render pieces
        for x in range(0,8):
            for y in range(0,8):
                bg = "white" if ((x+y)%2==0) else "grey"
                (pxl, pxr, pyu, pyd) = 1, 1, 1, 1
                if (y==0): pxl = 8
                if (x==0): pyu = 5
                lbl = tk.Label(master=self.__board, bg=bg,width=9,height=4, highlightbackground="grey", highlightthickness=1)
                lbl.grid(row=x,column=y, padx=(pxl,pxr), pady=(pyu,pyd))

                icon = None
                x = (7-x) if self.__board_rev else x
                g = gameboardapi.TryGetPiece(self.__GP1, x, y)
                if g is not None:
                    icon = IconMap1[g.PieceType()]
                else:
                    g = gameboardapi.TryGetPiece(self.__GP2, x, y)
                    if g is not None:
                        icon = IconMap2[g.PieceType()]

                if icon is not None:
                    tk_im = ImageTk.PhotoImage(icon)
                    lbl.configure(image=tk_im, width=65, height=65)
                    lbl.image = tk_im
                
                if self.selection.isAtMovingLoc(x, y):
                    lbl.config(highlightbackground = "red", highlightcolor= "red", highlightthickness=1)
                if self.selection.isSelected(x, y):
                    lbl.config(highlightbackground = "blue", highlightcolor= "blue", highlightthickness=1)
                
                lbl.bind("<Button-1>", lambda e, x=x, y=y, gp=g: self.__TK_HandleClick(x, y, gp))
        pass

    def __APISelectPieces(self, r, c, g):
        self.__uilock.acquire()
        self.selection.Set(r, c, g)
        # print(r,c,g.PID() if g is not None else None)
        self.__eventq.put_nowait(lambda: {
            self.__RenderBoard(),
            self.__setButtonsState(),
            self.__uilock.release()
        })

    def __APIMovePieces(self, cmd):
        self.__uilock.acquire()
        self.__setProgress(True)
        try:
            self.__lastgasused = None
            if cmd == "Withdraw" or cmd == "Pass":
                resp = self.api.MovePieces(0 if self.__CTX.turn %2 ==0 else 16,0,0,gameboardapi.SpecCommand[cmd])
            else :
                resp = self.api.MovePieces(self.selection.gamepiece.PID(),self.selection.r,self.selection.c, gameboardapi.SpecCommand[cmd])
            if resp is not None:
                self.__window.title("Chess Board - block: #"+str(resp["block_number"]))
                self.__lastgasused = resp["gas_used"]
        except Exception as e:
            messagebox.showerror("error", str(e))
        self.UpdateRefreshData()
        self.__eventq.put_nowait(lambda: {
            self.selection.Clear(),
            self.__RenderBoard(),
            self.__setButtonsState(),
            self.__setProgress(False),
            self.__uilock.release()
        })
    
    def __APIPollRefresh(self):
        self.__uilock.acquire()
        self.UpdateRefreshData()
        self.__eventq.put_nowait(lambda: {
            self.__RenderBoard(),
            self.__uilock.release()
        })
    
    def __TK_HandleClick(self, r, c, g):
        t = threading.Thread(target = self.__APISelectPieces, args=[r,c,g])
        t.daemon = True
        t.start()

    def __TK_HandleSubmit(self, cmd = "Null"):
        t = threading.Thread(target = self.__APIMovePieces, args=[cmd])
        t.daemon = True
        t.start()
    
    def __TK_HandleWin(self):
        self.__uilock.acquire()
        try:
            origb = self.api.Balance()
            resp = self.api.Win()
            newb = self.api.Balance()
            messagebox.showinfo("You Won!", "Balance: {newb} (+ {diff})\nGas used: {gas}".format(newb=newb, diff = newb-origb, gas = resp["gas_used"]))
        except Exception as e:
            messagebox.showerror("error", str(e))
        self.__uilock.release()

    ## run ui changes in ui thread
    def __After_Handlers(self):
        """To avoid UI from freezing, this function is to consume to completed tasks triggerred from buttons"""
        try:
            qitem = self.__eventq.get_nowait()
            qitem()
        except queue.Empty as e:
            pass
        self.__window.after(10, self.__After_Handlers)

    def __After_Poll(self):
        """Poll data from api which should be triggerred periodically"""
        if self.__refresh_thread is None or self.__refresh_thread.is_alive() == False:
            self.__refresh_thread = threading.Thread(target = self.__APIPollRefresh)
            self.__refresh_thread.daemon = True
            self.__refresh_thread.start()
        self.__window.after(10000, self.__After_Poll)
    
    def __on_closing(self):
        self.__window.destroy()