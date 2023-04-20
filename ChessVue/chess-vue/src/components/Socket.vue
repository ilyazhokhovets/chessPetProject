<template>
<div>

  <div>
  <input type="checkbox" value="record" id="checkbox" v-model="record" />
<label for="checkbox"> Режим обучения </label>
    </div>
  <div v-model="cp">
    Оценка позиции: {{ cp/100 }}
  </div>



<div id="myBoard" style="width: 400px"></div>
<button @click="flipBoard">Перевернуть доску</button> <br>
  <button :disabled="record" @click="hint">Подсказка</button> <br>
  <button @click="reset">Начать заново</button><br>
<!--   <ul>-->
<!--     <li v-for="elem in this.logs">-->
<!--       {{elem.r}}, {{elem.action || '-'}}, {{elem.status || '-'}}, {{elem.time || '-'}}, {{elem.fen}}-->

<!--     </li>-->
<!--   </ul>-->
{{pgn}}
  <div>

  <ul v-if="this.record ">
    <li v-for="elem in this.listMove">
      Ход:  {{ elem.move }}, {{ winPercent(elem).text}}  {{ winPercent(elem).value }},  Всего игр:  {{ elem.appearances }}, Оценка:  {{ elem.cp/100}}
	 </li>
    </ul>
</div>

  </div>

</template>

<script>

// import userimage from "@/assets/img/chesspieces/wikipedia/wK.png";
import  "@/chessboardjs/js/chessboard";
        import { Chess } from 'chess.js'
import Settings from "@/components/Settings";
export default {
  name: "Socket",
  components: {
    Settings
  },
  created() {
    this.connect()
  },
  mounted() {
  this.SuperPuper()

  },

  data() {
    return {
      username: '23232',
      source_fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      new_fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      move_uci: '',
      who_moved: '',
      record: false,
      listMove: [],
      game: '',
      board: '',
      color: 'w',
      status: 'disconnected',
      settings: '',
      cp: '0',
      pgn: '',
      win_percent: '',
      logs: [],
    }
    },

watch: {
    new_fen(){

      this.pgn = this.game.pgn()
      if (this.record && this.game.turn() === this.board.orientation().slice(0,1)) {

        this.sendSuggest()
      }
    },
  status(){
      if (this.status === 'connected') {
        this.reset()
      }
  }

},

  methods: {
    printLogs(){
      console.log(this.logs)
    },
    winPercent (elem){
      if (this.board.orientation()==='white'){
        return {text: 'Побед белых %',
          value: Math.round(elem.white_win*1000)/10
        }
      }
      return  {text: 'Побед черных %',
          value: Math.round(elem.black_win*1000)/10
        }
    },
    reset (){
      let fen = this.$store.getters.getSettings
      this.game.load(fen.startingFen)
      this.board.position(this.game.fen())

      this.record = false
      this.source_fen = fen
      this.new_fen = this.game.fen()

      if (this.game.turn() !== this.board.orientation().slice(0,1)){

        this.new_fen = this.game.fen()
        this.sendMove()

      }
      else{

      this.sendReset()
        }
    },
    hint (){
    let data = {
         action: 'hint',
        fen: this.new_fen,
      }

      this.chessSocket.send(JSON.stringify(data))
    },
    flipBoard(){
      this.board.flip()

      this.reset()
    },
  compMove (move_uci){
     var next_move = this.game.move({
            from: move_uci.slice(0, 2),
            to: move_uci.slice(2, 4),
            promotion: 'q'
          })
      this.fen = this.game.fen()
      this.board.position(this.game.fen())
    },

  onDrop (source, target) {
  // see if the move is legal
  this.source_fen = this.game.fen()
  try {
    var move = this.game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })
  }
  catch (error){
    move = null
  }

  // illegal move
  if (move === null) return 'snapback';
  this.new_fen = this.game.fen()
  this.move_uci = source+target
    this.listMove = []
    // this.sendCP()
  this.sendMove()
},


editCastleMove(uci){
   if (this.game.board()[0][4]!=null && this.game.board()[0][4]['type'] === 'k' && uci === 'e8h8') {
          uci= 'e8g8'
       }
   if (this.game.board()[0][4]!=null && this.game.board()[0][4]['type'] === 'k' && uci === 'e8a8') {
          uci= 'e8c8'
       }
   if (this.game.board()[7][4]!=null && this.game.board()[0][4]['type'] === 'k' && uci === 'e1h1') {
          uci= 'e1g1'
       }
   if (this.game.board()[7][4]!=null && this.game.board()[0][4]['type'] === 'k' && uci === 'e1a1') {
          uci= 'e1c1'
       }

   return uci
},


SuperPuper(){


  var board = null
var game = new Chess()



function onDragStart (source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over) return false

  // only pick up pieces for the side to move
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}




// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
}


var config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: this.onDrop,
  onSnapEnd: onSnapEnd
}

this.game = game
board = Chessboard('myBoard', config)
this.board = board

},


    connect() {
      this.chessSocket = new WebSocket(
          'ws://' + '127.0.0.1:8000/ws/chess/'
      );
      this.chessSocket.onopen = () => {
        this.status = "connected";

      }

      this.chessSocket.onmessage =  ({data}) => {
      var recieved_data = JSON.parse(data)

      recieved_data.r = 'response'
      console.log(recieved_data)
        this.logs.push(recieved_data)

        if (recieved_data.status === 'move') {
      this.getMove(recieved_data)
          }
         if (recieved_data.status === 'cp'){

       this.getCP(recieved_data)
        }
         if (recieved_data.status === 'hint'){
       this.printHint(recieved_data)
        }
         if (recieved_data.status === 'suggest'){
       this.getSuggest(recieved_data)
        }
         if (recieved_data.status === 'fail' || recieved_data.status === 'success' ){
       this.reset()
        }

         if (recieved_data.status === 'reset'){
       this.getReset(recieved_data)
        }
    }

    },

     printHint(recieved_data){
      alert(recieved_data.move_uci)
    },
     getMove(recieved_data){


          this.record = recieved_data.record
        this.source_fen = this.new_fen
        this.compMove(recieved_data.move_uci)
        this.new_fen = this.game.fen()
        this.who_moved = 'comp'

           this.sendCP()

        // else {
        //   this.reset()
        // }
    },

     getCP(recieved_data){

        this.cp = recieved_data.cp

    },

     sendCP(){
        let data = {
         action: 'sendCP',
        fen: this.new_fen,
      }
      data.r = 'request'
        this.logs.push(data)
       this.chessSocket.send(JSON.stringify(data))
    },
     sendSuggest(){
        let data = {
         action: 'sendSuggest',
        fen: this.new_fen,
          orientation: this.board.orientation()
      }
      data.r = 'request'
        this.logs.push(data)

       this.chessSocket.send(JSON.stringify(data))
    },
     getSuggest(recieved_data){
      this.listMove = recieved_data.listMove
    },
     sendReset(){
        let data = {
         action: 'reset',
        fen: this.new_fen,
      }
      data.r = 'request'
        this.logs.push(data)
       this.chessSocket.send(JSON.stringify(data))
    },
     getReset(recieved_data){
      this.record = recieved_data.record
       if (this.record){
         this.sendSuggest()
       }
    },

     sendMove (){

       let data = {
         action: 'sendMove',
        fen: this.new_fen,
        move: this.move_uci,
        source_fen: this.source_fen,
        record: this.record,
         settings: this.$store.getters.getSettings
      }
      data.r = 'request'
        this.logs.push(data)
       this.chessSocket.send(JSON.stringify(data))
    },

  }



}
</script>

<style scoped>
@import "@/assets/css/chessboard-1.0.0.css"
</style>