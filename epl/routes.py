from epl import app, db
from epl.models import Club, Player
from flask import render_template, redirect, url_for, request, flash, abort
from sqlalchemy.exc import IntegrityError

@app.route('/')
def index():
    return render_template('index.html', title='EPL Home')

# ---------- CLUB ----------
@app.route('/clubs')
def all_clubs():
    clubs = db.session.query(Club).all()
    return render_template('clubs/index.html', title='Clubs', clubs=clubs)

@app.route('/clubs/new', methods=['GET', 'POST'])
def new_club():
    if request.method == 'POST':
        name = request.form['name'].strip()
        stadium = request.form['stadium'].strip()
        year_raw = request.form['year'].strip()
        logo = request.form['logo'].strip()

        if not year_raw.isdigit():
            flash('Year ต้องเป็นตัวเลข', 'danger')
            return redirect(url_for('new_club'))

        if Club.query.filter_by(name=name).first():
            flash('ชื่อสโมสรนี้มีอยู่แล้ว', 'danger')
            return redirect(url_for('new_club'))

        club = Club(
            name=name,
            stadium=stadium,
            year=int(year_raw),
            logo=logo
        )

        try:
            db.session.add(club)
            db.session.commit()
            flash(f'Club {name} has been created!', 'success')
            return redirect(url_for('all_clubs'))
        except IntegrityError:
            db.session.rollback()
            flash('เกิดข้อผิดพลาดในการบันทึกข้อมูล', 'danger')
            return redirect(url_for('new_club'))

    return render_template('clubs/new_club.html', title='New Club')

@app.route('/clubs/search', methods=['GET', 'POST'])
def search_clubs():
    if request.method == 'POST':
        club_name = request.form.get('club_name', '').strip()
        return redirect(url_for('search_clubs', club_name=club_name))

    club_name = request.args.get('club_name', '').strip()
    clubs = (
        db.session.scalars(
            db.select(Club).where(Club.name.ilike(f'%{club_name}%'))
        ).all()
        if club_name else []
    )

    return render_template(
        'clubs/search_club.html',
        title='Search Clubs',
        clubs=clubs,
        club_name=club_name
    )

@app.route('/clubs/<int:club_id>/info')
def club_info(club_id):
    club = Club.query.get_or_404(club_id)
    return render_template('clubs/info_club.html', title=club.name, club=club)

@app.route('/clubs/<int:club_id>/update', methods=['GET', 'POST'])
def update_club(club_id):
    club = Club.query.get_or_404(club_id)

    if request.method == 'POST':
        club.name = request.form.get('name', '').strip()
        club.stadium = request.form.get('stadium', '').strip()
        club.year = int(request.form.get('year', club.year))
        club.logo = request.form.get('logo', '').strip()

        db.session.commit()
        flash('Club updated successfully!', 'success')
        return redirect(url_for('club_info', club_id=club.id))

    return render_template('clubs/update_club.html', title='Update Club', club=club)


# ------------------ PLAYER ------------------

@app.route('/players')
def all_players():
    players = db.session.query(Player).all()
    return render_template('player/index.html', title='Players', players=players)

@app.route('/players/search', methods=['POST'])
def search_players():
    player_name = request.form.get('player_name', '').strip()

    if player_name:
        players = db.session.scalars(
            db.select(Player).where(Player.name.ilike(f'%{player_name}%'))
        ).all()
    else:
        players = db.session.query(Player).all()

    # คืน “แถวตาราง” ไปอัปเดตใน #result (HTMX)
    return render_template('player/search_player.html', players=players)

@app.route('/players/<int:player_id>/info')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player/info_player.html', title=player.name, player=player)

@app.route('/players/new', methods=['GET', 'POST'])
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

        if not club_id_raw.isdigit():
            flash('กรุณาเลือกสโมสร', 'danger')
            return redirect(url_for('new_player'))

        goal = int(goal_raw) if goal_raw.isdigit() else 0
        squad_no = int(squad_raw) if squad_raw.isdigit() else None
        club_id = int(club_id_raw)

        player = Player(
            name=name,
            position=position,
            nationality=nationality,
            goal=goal,
            squad_no=squad_no,
            img=img,
            club_id=club_id
        )

        try:
            db.session.add(player)
            db.session.commit()
            flash('New player added successfully!', 'success')
            return redirect(url_for('all_players'))
        except IntegrityError:
            db.session.rollback()
            flash('บันทึกไม่สำเร็จ (ข้อมูลอาจซ้ำ/ไม่ถูกต้อง)', 'danger')
            return redirect(url_for('new_player'))

    return render_template('player/new_player.html', title='New Player', clubs=clubs)

@app.route('/players/<int:player_id>/update', methods=['GET', 'POST'])
def update_player(player_id):
    player = Player.query.get_or_404(player_id)
    clubs = db.session.query(Club).all()

    if request.method == 'POST':
        player.position = request.form.get('position', player.position).strip()
        player.nationality = request.form.get('nationality', player.nationality).strip()
        player.img = request.form.get('img', player.img).strip()

        goal_raw = request.form.get('goal', str(player.goal)).strip()
        squad_raw = request.form.get('squad_no', '').strip()
        club_id_raw = request.form.get('club_id', str(player.club_id)).strip()

        player.goal = int(goal_raw) if goal_raw.isdigit() else player.goal
        player.squad_no = int(squad_raw) if squad_raw.isdigit() else None

        if club_id_raw.isdigit():
            player.club_id = int(club_id_raw)

        try:
            db.session.commit()
            flash('Player updated successfully!', 'success')
            return redirect(url_for('player_detail', player_id=player.id))
        except IntegrityError:
            db.session.rollback()
            flash('อัปเดตไม่สำเร็จ', 'danger')
            return redirect(url_for('update_player', player_id=player.id))

    return render_template('player/update_player.html', title='Update Player', player=player, clubs=clubs)