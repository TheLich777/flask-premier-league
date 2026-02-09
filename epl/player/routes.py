from flask import Blueprint, render_template, redirect, url_for, flash, request
from epl.models import Player, Club
from epl.extension import db

players_bp = Blueprint('players', __name__, template_folder='templates')

@players_bp.route('/')
def all_players():
    players = db.session.query(Player).all()
    return render_template('player/index.html', players=players, title='Players')


@players_bp.route('/new', methods=['GET', 'POST'])
def new_player():
    clubs = db.session.query(Club).all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        position = request.form.get('position', '').strip()
        nationality = request.form.get('nationality', '').strip()
        goal_raw = request.form.get('goal', '0').strip()
        squad_raw = request.form.get('squad_no', '').strip()
        img = request.form.get('img', '').strip()
        club_id_raw = request.form.get('club_id', '').strip()

        if not name:
            flash('กรุณากรอกชื่อผู้เล่น', 'danger')
            return redirect(url_for('players.new_player'))

        if not club_id_raw.isdigit():
            flash('กรุณาเลือกสโมสร', 'danger')
            return redirect(url_for('players.new_player'))

        goal = int(goal_raw) if goal_raw.isdigit() else 0
        squad_no = int(squad_raw) if squad_raw.isdigit() else None

        player = Player(
            name=name,
            position=position,
            nationality=nationality,
            goal=goal,
            squad_no=squad_no,
            img=img,
            club_id=int(club_id_raw)
        )

        db.session.add(player)
        db.session.commit()
        flash('เพิ่มผู้เล่นเรียบร้อย', 'success')
        return redirect(url_for('players.all_players'))

    return render_template('player/new_player.html', title='New Player', clubs=clubs)


@players_bp.route('/search', methods=['POST'])
def search_players():
    player_name = request.form.get('player_name', '').strip()

    if player_name:
        players = db.session.query(Player).filter(Player.name.ilike(f'%{player_name}%')).all()
    else:
        players = db.session.query(Player).all()

    return render_template('player/search_player.html', players=players)


@players_bp.route('/<int:player_id>/info')
def player_info(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player/info_player.html', title=player.name, player=player)


@players_bp.route('/<int:player_id>/update', methods=['GET', 'POST'])
def update_player(player_id):
    player = Player.query.get_or_404(player_id)
    clubs = db.session.query(Club).all()

    if request.method == 'POST':
        player.name = request.form.get('name', player.name).strip()
        player.position = request.form.get('position', player.position).strip()
        player.nationality = request.form.get('nationality', player.nationality).strip()
        player.img = request.form.get('img', player.img).strip()

        goal_raw = request.form.get('goal', str(player.goal)).strip()
        squad_raw = request.form.get('squad_no', '').strip()
        club_id_raw = request.form.get('club_id', str(player.club_id)).strip()

        if goal_raw.isdigit():
            player.goal = int(goal_raw)
        player.squad_no = int(squad_raw) if squad_raw.isdigit() else None
        if club_id_raw.isdigit():
            player.club_id = int(club_id_raw)

        db.session.commit()
        flash('อัปเดตผู้เล่นเรียบร้อย', 'success')
        return redirect(url_for('players.player_info', player_id=player.id))

    return render_template('player/update_player.html', title='Update Player', player=player, clubs=clubs)
