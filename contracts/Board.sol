// SPDX-License-Identifier: GPL-2.0
pragma solidity >=0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/utils/Strings.sol";

// Board Contract allows Earning Ether (bet) for Winning the game
contract Board {

    enum PieceType{
        king, rook, bishop, queen, knight, pawn
    }

    enum PieceID {
        p1_king, p1_queen, p1_rookl, p1_rookr, p1_bishopl, p1_bishopr, p1_knightl, p1_knightr, p1_pawn1, p1_pawn2, p1_pawn3, p1_pawn4, p1_pawn5, p1_pawn6, p1_pawn7, p1_pawn8,
        p2_king, p2_queen, p2_rookl, p2_rookr, p2_bishopl, p2_bishopr, p2_knightl, p2_knightr, p2_pawn1, p2_pawn2, p2_pawn3, p2_pawn4, p2_pawn5, p2_pawn6, p2_pawn7, p2_pawn8,
        Nil
    }

    enum SpecCommand {
        Null, Withdraw, Pass, Castle, PromoteToQueen, PromoteToRook, PromoteToBishop, PromoteToKnight
    }

    enum PlayerState {
        Normal,
        Withdraw,
        Pass
    }

    struct GamePiece {
        PieceID pid;
        PieceType ptype;
        uint8 r;
        uint8 c;
        bool alive;
        uint256 moves;
    }

    function GamePieceStr(GamePiece memory gp) private view returns (string memory) {
        string memory pid = Strings.toString(uint256(gp.pid));
        string memory ptype = Strings.toString(uint256(gp.ptype));
        string memory r = Strings.toString(gp.r);
        string memory c = Strings.toString(gp.c);
        string memory alive = gp.alive ? "1" : "0";
        return string(abi.encodePacked("(",pid, ",", ptype, ",", r,",",c,",",alive,")"));
    }

    struct Player {
        address player_address;
        PlayerState state;
        uint256 bet;
    }

    struct Context {  
        Player PlayerOne;
        Player PlayerTwo;
        uint256 fee;
        int playerturn;
    }

    Context public ctx; // game context
    PieceID lastPieceInd;
    mapping(PieceID => GamePiece) Pieces;
    PieceID[8][8] Squares;

    
    modifier CheckOutOfBoard (uint8 row, uint8 col) {
        require (row >= 0 && row <= 7 && col >= 0 && col <= 7, "Position Out of Board");
        _;
    }

    modifier CheckTurn(PieceID pid){
        require(pid != PieceID.Nil, "Invalid Input: PieceID");
        require((ctx.playerturn%2==0)?isP1(pid):isP2(pid), "Cannot move opponent's pieces!");
        if (ctx.PlayerOne.player_address != address(0) && ctx.PlayerTwo.player_address != address(0)){
            require(((ctx.playerturn%2 == 0) && address(msg.sender) == ctx.PlayerOne.player_address) 
                    || ((ctx.playerturn%2 != 0) && address(msg.sender) == ctx.PlayerTwo.player_address), "Not Your Turn");
        }
         _;
    }

    modifier GameCanPlay() {
        require(ctx.PlayerOne.state != PlayerState.Withdraw && ctx.PlayerTwo.state != PlayerState.Withdraw, "Game no longer valid");
        require(ctx.PlayerOne.state != PlayerState.Pass || ctx.PlayerTwo.state != PlayerState.Pass, "Game has finished without winner");
        bool validP1 = ctx.PlayerOne.player_address == address(0);
        bool validP2 = ctx.PlayerTwo.player_address == address(0);
        require((validP1 && validP2) || (!validP1 && !validP2), "Cannot play without component");
        _;
    }

    constructor() {
        for(uint256 i=0;i<8;i++)
        for(uint256 j=0;j<8;j++)
            Squares[i][j] = PieceID.Nil;
        
        Pieces[PieceID.p1_king] = GamePiece(PieceID.p1_king,PieceType.king,0,4,true,0); Squares[0][4] = PieceID.p1_king;
        Pieces[PieceID.p1_queen] = GamePiece(PieceID.p1_queen,PieceType.queen,0,3,true,0); Squares[0][3] = PieceID.p1_queen;
        Pieces[PieceID.p1_rookl] = GamePiece(PieceID.p1_rookl,PieceType.rook,0,0,true,0); Squares[0][0] = PieceID.p1_rookl;
        Pieces[PieceID.p1_rookr] = GamePiece(PieceID.p1_rookr,PieceType.rook,0,7,true,0); Squares[0][7] = PieceID.p1_rookr;
        Pieces[PieceID.p1_bishopl] = GamePiece(PieceID.p1_bishopl,PieceType.bishop,0,2,true,0); Squares[0][2] = PieceID.p1_bishopl;
        Pieces[PieceID.p1_bishopr] = GamePiece(PieceID.p1_bishopr,PieceType.bishop,0,5,true,0); Squares[0][5] = PieceID.p1_bishopr;
        Pieces[PieceID.p1_knightl] = GamePiece(PieceID.p1_knightl,PieceType.knight,0,1,true,0); Squares[0][1] = PieceID.p1_knightl;
        Pieces[PieceID.p1_knightr] = GamePiece(PieceID.p1_knightr,PieceType.knight,0,6,true,0); Squares[0][6] = PieceID.p1_knightr;
        for (uint256 i = 0;i<8;i++) {
            PieceID pid = PieceID(uint256(PieceID.p1_pawn1) + i);
            Pieces[pid] = GamePiece(pid,PieceType.pawn,1,uint8(i),true,0); Squares[1][i] = pid;
        }

        Pieces[PieceID.p2_king] = GamePiece(PieceID.p2_king,PieceType.king,7,4,true,0); Squares[7][4] = PieceID.p2_king;
        Pieces[PieceID.p2_queen] = GamePiece(PieceID.p2_queen,PieceType.queen,7,3,true,0); Squares[7][3] = PieceID.p2_queen;
        Pieces[PieceID.p2_rookl] = GamePiece(PieceID.p2_rookl,PieceType.rook,7,0,true,0); Squares[7][0] = PieceID.p2_rookl;
        Pieces[PieceID.p2_rookr] = GamePiece(PieceID.p2_rookr,PieceType.rook,7,7,true,0); Squares[7][7] = PieceID.p2_rookr;
        Pieces[PieceID.p2_bishopl] = GamePiece(PieceID.p2_bishopl,PieceType.bishop,7,2,true,0); Squares[7][2] = PieceID.p2_bishopl;
        Pieces[PieceID.p2_bishopr] = GamePiece(PieceID.p2_bishopr,PieceType.bishop,7,5,true,0); Squares[7][5] = PieceID.p2_bishopr;
        Pieces[PieceID.p2_knightl] = GamePiece(PieceID.p2_knightl,PieceType.knight,7,1,true,0); Squares[7][1] = PieceID.p2_knightl;
        Pieces[PieceID.p2_knightr] = GamePiece(PieceID.p2_knightr,PieceType.knight,7,6,true,0); Squares[7][6] = PieceID.p2_knightr;
        for (uint256 i = 0;i<8;i++) {
            PieceID pid = PieceID(uint256(PieceID.p2_pawn1) + i);
            Pieces[pid] = GamePiece(pid,PieceType.pawn,6,uint8(i),true,0); Squares[6][i] = pid;
        }
    }
    
    function abs(uint8 s, uint8 e) private pure returns (uint8) { return (s>e) ? (s-e) : (e-s); }
    function isP1(PieceID pid) private pure returns (bool) { return uint256(pid) >= 0 && uint256(pid)<=15;}
    function isP2(PieceID pid) private pure returns (bool) { return uint256(pid) >= 16 && uint256(pid)<=31;}
    function isSameP(PieceID pid1, PieceID pid2) private pure returns (bool) { return (isP1(pid1) && isP1(pid2)) || (isP2(pid1) && isP2(pid2));}

    // assume either ling or diag, and r1!=r2 || c1!=c2
    // check blocking exclusively
    function checkBlocked(uint8 r1, uint8 c1, uint8 r2, uint8 c2) private view returns (bool) {
        bool change_col = true;
        bool change_row = true;
        if (r1==r2&&c1!=c2) change_row = false; // row line
        else if (r1!=r2&&c1==c2) change_col = false; // col line
        // else diagonal

        if (change_col) { if (c1 > c2) c1--; else c1++; }
        if (change_row) { if (r1 > r2) r1--; else r1++; }
        while((!change_row && c1!=c2) || (change_row && r1!=r2)){
            if (Squares[r1][c1]!=PieceID.Nil) {if(Pieces[Squares[r1][c1]].alive) return true;}   
            if (change_col) { if (c1 > c2) c1--; else c1++; }
            if (change_row) { if (r1 > r2) r1--; else r1++; }
        }
        return false;
    }

    function capturePiece(PieceID pid) private {
        Pieces[pid].alive = false;
        Squares[Pieces[pid].r][Pieces[pid].c] = PieceID.Nil;
        // loss the game if king is captured
        if (pid == PieceID.p1_king) {
            ctx.PlayerOne.state = PlayerState.Withdraw;
        } else if (pid == PieceID.p2_king) {
            ctx.PlayerTwo.state = PlayerState.Withdraw;
        }
    }

    function movePiece(PieceID pid, uint8 r, uint8 c) private {
        Squares[Pieces[pid].r][Pieces[pid].c] = PieceID.Nil;
        Pieces[pid].r = r;
        Pieces[pid].c = c;
        Pieces[pid].moves ++;
        Squares[r][c] = pid;
    }

    function MovePawn(PieceID pid, uint8 r, uint8 c, PieceType promotype) private {
        uint8 srow = Pieces[pid].r;
        uint8 scol = Pieces[pid].c;
        bool isp1 = isP1(pid);
        bool isforward1 = (isp1? r > srow : srow > r) && abs(r, srow) == 1 && scol == c;
        bool isforward2 = (isp1? r > srow : srow > r) && abs(r, srow) == 2 && scol == c;
        bool isdiag = isp1? ((r > srow) && abs(r, srow) == 1 && abs(c, scol) == 1)
                            : ((r < srow) && abs(r, srow) == 1 && abs(c, scol) == 1);
        PieceID Hit;

        require(!(scol != c && !isdiag), "invalid move");
        require(!(!isforward1 && !isforward2 && !isdiag), "invalid move");
        if (promotype!=PieceType.pawn) require(isp1?(r==7):(r==0), "Not a promotion square");

        // check pawn destination
        if (isforward1 || isforward2) {
            Hit = Squares[r][scol];
            require(Hit==PieceID.Nil, "blocked");
        }
        if (isforward2) {
            require(Pieces[pid].moves == 0, "only move 2 steps on first move");
            Hit = Squares[isp1?(r-1):(r+1)][scol];
            require(Hit==PieceID.Nil, "blocked");
        }
        if (isdiag) { // capture
            // En passant?
            bool isEnPassant = false;
            Hit = Squares[srow][c];
            if (Hit != PieceID.Nil && !isSameP(pid, Hit)) {
                isEnPassant = (Pieces[Hit].ptype == PieceType.pawn && Pieces[Hit].moves == 1 && Hit == lastPieceInd) 
                            && ((isp1 && srow == 4) || (!isp1 && srow == 3));
            }
            if (!isEnPassant) { // normal capture
                Hit = Squares[r][c];
            }
            require(Hit != PieceID.Nil && Pieces[Hit].alive, "Must capture or En passant for diagonal move");
            require(!isSameP(pid,Hit), "blocked");
            capturePiece(Hit);
        }

        movePiece(pid, r, c);
        // Promotion
        if (promotype!=PieceType.pawn) {
            Pieces[pid].ptype = promotype;
        }
    }

    function ValidateMoveRook(uint8 srow, uint8 scol, uint8 r, uint8 c) private returns (bool){
        require(srow == r || scol == c, "Invalid move");
        require(!checkBlocked(srow, scol, r, c), "blocked");
        return true;
    }

    function ValidateRookCastling(PieceID pid, uint8 r, uint8 c) private  {
        uint8 srow = Pieces[pid].r;
        uint8 scol = Pieces[pid].c;

        PieceID kingID = isP1(pid)?PieceID.p1_king:PieceID.p2_king;
        require(Pieces[pid].moves == 0 && Pieces[kingID].moves == 0, "Invalid castling: Should have no previous move.");
        require(!checkBlocked(srow, scol, Pieces[kingID].r, Pieces[kingID].c), "Invalid castling: Should have no pieces between rook and king.");

        if (Pieces[pid].c < Pieces[kingID].c) {
            movePiece(pid, srow, scol+3);
            movePiece(kingID, srow, scol+2);
        } else {
            movePiece(pid, srow, scol-2);
            movePiece(kingID, srow, scol-1);
        }
    }

    function ValidateMoveKnight(uint8 srow, uint8 scol,  uint8 r, uint8 c) private returns (bool){
        require((abs(r, srow)==1 && abs(c, scol)==2)||(abs(r,srow)==2 && abs(c,scol)==1), "Invalid Move");
        return true;
    }

    function ValidateMoveBishop(uint8 srow, uint8 scol,  uint8 r, uint8 c) private returns (bool) {
        require(abs(r, srow) == abs(c, scol), "Invalid Move");
        require(!checkBlocked(srow, scol, r, c), "blocked");
        return true;
    }

    function ValidateMoveQueen(uint8 srow, uint8 scol, uint8 r, uint8 c) private returns (bool) {
        require((c == scol)
                || (r == srow) 
                || (abs(srow, r) == abs(scol, c)), "Invalid Move");
        require(!checkBlocked(srow, scol, r, c), "blocked");
        return true;
    }

    function ValidateMoveKing(uint8 srow, uint8 scol, uint8 r, uint8 c) private returns (bool) {
        require(abs(srow, r)<=1 && abs(scol, c)<=1, "Invalid Move");
        require(!checkBlocked(srow, scol, r, c), "blocked");
        return true;
    }

    function Win() public payable {
        require(address(msg.sender) == ctx.PlayerOne.player_address || address(msg.sender) == ctx.PlayerTwo.player_address, "You did not join the game ever!");

        if (address(msg.sender) == ctx.PlayerOne.player_address && ctx.PlayerOne.state != PlayerState.Withdraw && ctx.PlayerTwo.state == PlayerState.Withdraw) {
            payable(msg.sender).send(ctx.PlayerOne.bet + ctx.PlayerTwo.bet);
        } else if (address(msg.sender) == ctx.PlayerTwo.player_address && ctx.PlayerTwo.state != PlayerState.Withdraw && ctx.PlayerOne.state == PlayerState.Withdraw) {
            payable(msg.sender).send(ctx.PlayerOne.bet + ctx.PlayerTwo.bet);
        } else if (address(msg.sender) == ctx.PlayerOne.player_address && ctx.PlayerOne.state == PlayerState.Pass && ctx.PlayerTwo.state == PlayerState.Pass) {
            if (payable(msg.sender).send(ctx.PlayerOne.bet)){
                ctx.PlayerOne.bet = 0;
            }
        } else if (address(msg.sender) == ctx.PlayerTwo.player_address && ctx.PlayerTwo.state == PlayerState.Pass && ctx.PlayerOne.state == PlayerState.Pass) {
            if (payable(msg.sender).send(ctx.PlayerTwo.bet)){
                ctx.PlayerTwo.bet = 0;
            }
        } else {
            revert("You did not win the game yet!");
        }
    }

    function JoinGame(uint256 minEntryFee) public payable {
        require(ctx.PlayerOne.player_address == address(0) || ctx.PlayerTwo.player_address == address(0), "Game already full");
        require(ctx.playerturn == 0, "Game already started");
        if (ctx.PlayerOne.player_address == address(0)) {
            require(minEntryFee <= msg.value, "Cannot set entry fee > amount of bet");
            ctx.PlayerOne.player_address = address(msg.sender);
            ctx.PlayerOne.bet = msg.value;
            ctx.fee = minEntryFee;
        } else {
            require(ctx.PlayerOne.player_address != address(msg.sender), "cannot join again as player two");
            require(msg.value >= ctx.fee, "EntryFee is not enough to join this game");
            ctx.PlayerTwo.player_address = address(msg.sender);
            ctx.PlayerTwo.bet = msg.value;
        }
    }
    
    function GetPiecesInfo() public view returns (string memory) {
        bytes memory ret = abi.encodePacked("[", GamePieceStr(Pieces[PieceID(0)]));
        for(uint256 i = 1;i<32;i++) {
            ret = abi.encodePacked(ret,",",GamePieceStr(Pieces[PieceID(i)]));
        }
        ret = abi.encodePacked(ret,"]");
        return string(ret);
    }

    function MovePiece(PieceID pid, uint8 pos_r, uint8 pos_c, uint256 speccmd) 
            GameCanPlay CheckTurn(pid) CheckOutOfBoard(pos_r,pos_c)  public {
        GamePiece storage thep = Pieces[pid];
        Player storage thePlayer = ctx.playerturn%2==0? ctx.PlayerOne: ctx.PlayerTwo;
        Player storage theOtherPlayer = ctx.playerturn%2==0? ctx.PlayerTwo: ctx.PlayerOne;
        PieceID Hit;
        bool isMove=false;

        require(thep.alive, "this piece is captured");
        require(thep.r != pos_r || thep.c != pos_c, "cannot move to original place");

        // handle special command before move
        if (theOtherPlayer.state == PlayerState.Pass) {
            if (speccmd != uint256(SpecCommand.Pass)) { // not agree on tie
                theOtherPlayer.state = PlayerState.Normal;
                ctx.playerturn++;
                return;
            }
        }
        if (speccmd == uint256(SpecCommand.Withdraw)) {
            thePlayer.state = PlayerState.Withdraw;
            return;
        } else if (speccmd == uint256(SpecCommand.Pass)){
            thePlayer.state = PlayerState.Pass;
            ctx.playerturn++;
            return;
        }

        if (thep.ptype == PieceType.pawn){
            PieceType reqPtype = PieceType.pawn;
            if (speccmd == uint256(SpecCommand.PromoteToQueen)) reqPtype = PieceType.queen;
            else if (speccmd == uint256(SpecCommand.PromoteToBishop)) reqPtype = PieceType.bishop;
            else if (speccmd == uint256(SpecCommand.PromoteToKnight)) reqPtype = PieceType.knight;
            else if (speccmd == uint256(SpecCommand.PromoteToRook)) reqPtype = PieceType.rook;
            MovePawn(pid, pos_r, pos_c, reqPtype);
            thep.ptype = reqPtype;
        } else if (thep.ptype == PieceType.rook) {
            if (speccmd == uint256(SpecCommand.Castle)) {
                ValidateRookCastling(pid, pos_r, pos_c);
            } else {
                isMove = ValidateMoveRook(thep.r, thep.c, pos_r, pos_c);
            }
        } else if (thep.ptype == PieceType.knight){
            isMove = ValidateMoveKnight(thep.r, thep.c, pos_r, pos_c);
        } else if (thep.ptype == PieceType.bishop) {
            isMove = ValidateMoveBishop(thep.r, thep.c, pos_r, pos_c);
        } else if (thep.ptype == PieceType.queen) {
            isMove = ValidateMoveQueen(thep.r, thep.c, pos_r, pos_c);
        } else if (thep.ptype == PieceType.king) {
            isMove = ValidateMoveKing(thep.r, thep.c, pos_r, pos_c);
        }

        if (isMove) {
            Hit = Squares[pos_r][pos_c];
            if (Hit != PieceID.Nil && Pieces[Hit].alive) { // Hit a piece
                require(!isSameP(pid,Hit), "blocked");
                capturePiece(Hit);
            }
            movePiece(pid, pos_r, pos_c);
        }

        lastPieceInd = pid;
        ctx.playerturn++;
    }

}