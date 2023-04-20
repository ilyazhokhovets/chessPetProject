
import numpy
from .models import *
from .lichess_api import top_moves_eval, get_next_fen, move_info, legal_moves


def _delete_db():
    obj = Position.objects.all()
    obj.delete()
    obj = Training.objects.all()
    obj.delete()


class Processing:
    def __init__(self, data):
        self.record = data['record']
        self.move_uci = data['move']
        self.initial_fen = data['source_fen']
        self.new_fen = data['fen']
        self.settings = data['settings']
        self.status = 'move'
        self.response_move = None

    def _is_move_correct(self):

        training_obj = Training.objects.filter(move__initial_fen__fen=self.initial_fen, move__uci=self.move_uci)

        return len(training_obj) > 0

    def _finish_run(self, success: bool):

        self.status = ['fail', 'success'][success]

    def _make_move(self):
        move_obj_list = Move.objects.filter(initial_fen__fen=self.new_fen)

        pos_info = [p.new_fen.positioninfo.appearances for p in move_obj_list]

        appearances = []
        total = 0
        for appearance_value in pos_info:

            appearances.append(appearance_value or 0)
            total += appearance_value or 0

        proba = [appearance_value / total for appearance_value in appearances]
        choice = int(numpy.random.choice(numpy.arange(0, len(move_obj_list)), p=proba))

        self.response_move =  move_obj_list[choice].uci

    def _settings_check(self) -> bool:
        #TODO
        x = Position.objects.filter(fen=self.initial_fen,
                                    positionparsed__n_moves__lte=int(self.settings['maxDepth']),)
                                    # positioninfo__cp__range=(int(self.settings['maxCpBlack']), int(self.settings['maxCpWhite'])),
                                    # positioninfo__appearances__gt=int(self.settings['minAppearancePercentTotal']))

        return len(x)>0

    def _update_training(self):

        move = Move.objects.filter(initial_fen__fen=self.initial_fen, uci=self.move_uci).get()

        training_obj_tuple = Training.objects.get_or_create(move=move)
        if training_obj_tuple[1]:
            training_obj_tuple[0].save()
            training_stats_obj = TrainingStats(training_obj=training_obj_tuple[0])
            training_stats_obj.save()

    def _create_children_fens(self):

        pos_obj = Position.objects.filter(fen=self.new_fen).get()

        next_move_list = move_info(self.new_fen)
        next_move_eval = top_moves_eval(self.new_fen)

        for move in legal_moves(self.new_fen):
            fen = get_next_fen(self.new_fen, move)
            new_pos_obj = Position.objects.get_or_create(fen=fen)

            if new_pos_obj[1]:
                new_pos_obj[0].save()
                pos_parsed_obj = PositionParsed(fen=new_pos_obj[0])
                pos_parsed_obj.save()

            move_obj = Move.objects.get_or_create(initial_fen=pos_obj, uci=move, new_fen=new_pos_obj[0])
            if move_obj[1]: move_obj[0].save()

            try:
                ww_percent = next_move_list[move]['white'] / next_move_list[move]['times_played']
                bw_percent = next_move_list[move]['black'] / next_move_list[move]['times_played']

            except KeyError:
                ww_percent = None
                bw_percent = None

            pos_info_obj = PositionInfo.objects.get_or_create(fen=new_pos_obj[0])

            if pos_info_obj[1]:
                try:
                    pos_info_obj[0].appearances = next_move_list[move]['times_played']

                except KeyError:
                    pos_info_obj[0].appearances = None

                pos_info_obj[0].white_win_percent = ww_percent
                pos_info_obj[0].black_win_percent = bw_percent
                try:
                    pos_info_obj[0].cp = next_move_eval[move]['Centipawn']
                    pos_info_obj[0].mate = next_move_eval[move]['Mate']
                except KeyError:
                    pos_info_obj[0].cp = None
                    pos_info_obj[0].mate = None
                pos_info_obj[0].save()

    def _training_handler(self):
        if self._is_move_correct():
            if not self._settings_check():
                self._finish_run(success=True)
            else:
                if Training.objects.filter(move__uci=self.move_uci).exists():
                    self.status = 'move'
                    self._make_move()
                    next_fen = get_next_fen(self.new_fen, self.response_move)
                    if Training.objects.filter(move__initial_fen__fen=next_fen).exists():
                        self.record = False
                    else:
                        self.record = True
                else:
                    self._finish_run(success=True)
                    self.record = True
        else:
            self._finish_run(success=False)

    def _record_handler(self):

        if self._settings_check():
            self._create_children_fens()
            self._update_training()
            self._make_move()
        else:
            self.record = False
            self.status = 'success'

    def get_response(self):
        if self.new_fen == self.settings['startingFen']:
            self._create_children_fens()
            self._make_move()
            next_fen = get_next_fen(self.new_fen, self.response_move)

            if Training.objects.filter(move__initial_fen__fen=next_fen).exists():
                self.record = False
            else:
                self.record = True

        else:
            if self.record:
                self._record_handler()
            else:
                self._training_handler()


class Suggest:
    def __init__(self, data):
        self.suggestion = []
        self.new_fen = data['fen']
        self.white_move = data['orientation'] == 'white'

    def _create_children_fens(self):

        pos_obj = Position.objects.get_or_create(fen=self.new_fen)
        if pos_obj[1]:
            pos_obj[0].save()
            pos_parsed_obj = PositionParsed(fen=pos_obj[0])
            pos_parsed_obj.save()
        pos_obj = pos_obj[0]
        next_move_list = move_info(self.new_fen)
        next_move_eval = top_moves_eval(self.new_fen)
        for move in next_move_list.keys():
            fen = get_next_fen(self.new_fen, move)
            new_pos_obj = Position.objects.get_or_create(fen=fen)

            if new_pos_obj[1]:
                new_pos_obj[0].save()
                pos_parsed_obj = PositionParsed(fen=new_pos_obj[0])
                pos_parsed_obj.save()

            move_obj = Move.objects.get_or_create(initial_fen=pos_obj, uci=move, new_fen=new_pos_obj[0])
            if move_obj[1]: move_obj[0].save()
            ww_percent = next_move_list[move]['white'] / next_move_list[move]['times_played']
            bw_percent = next_move_list[move]['black'] / next_move_list[move]['times_played']
            pos_info_obj = PositionInfo.objects.get_or_create(fen=new_pos_obj[0])

            if pos_info_obj[1]:
                pos_info_obj[0].appearances = next_move_list[move]['times_played']
                pos_info_obj[0].white_win_percent = ww_percent
                pos_info_obj[0].black_win_percent = bw_percent
                try:
                    pos_info_obj[0].cp = next_move_eval[move]['Centipawn']
                    pos_info_obj[0].mate = next_move_eval[move]['Mate']
                except KeyError:
                    pos_info_obj[0].cp = None
                    pos_info_obj[0].mate = None
                pos_info_obj[0].save()

    def create_list(self):
        move_obj = Move.objects.filter(initial_fen__fen=self.new_fen, new_fen__positioninfo__cp__isnull=False )
        self._create_children_fens()

        for move in move_obj:

            self.suggestion.append({'move': move.uci,
                                    'white_win': move.new_fen.positioninfo.white_win_percent,
                                    'black_win':move.new_fen.positioninfo.black_win_percent,
                                    'appearances': move.new_fen.positioninfo.appearances,
                                    'cp': move.new_fen.positioninfo.cp})
        self.suggestion.sort(key=lambda x: x['cp'], reverse=self.white_move)
        return self.suggestion[:5]
