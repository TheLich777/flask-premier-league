from flask import Blueprint, render_template, redirect, url_for, request, flash
from epl.models import Club
from epl.extension import db

clubs_bp = Blueprint('clubs', __name__, template_folder='templates')

@clubs_bp.route('/')
def all_clubs():
    clubs = db.session.query(Club).all()
    return render_template('clubs/index.html', clubs=clubs, title='Clubs')

@clubs_bp.route('/new', methods=['GET', 'POST'])
def new_club():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        stadium = request.form.get('stadium', '').strip()
        year_raw = request.form.get('year', '').strip()
        logo = request.form.get('logo', '').strip()

        if not name:
            flash('กรุณากรอกชื่อสโมสร', 'danger')
            return redirect(url_for('clubs.new_club'))

        year = int(year_raw) if year_raw.isdigit() else None

        club = Club(name=name, stadium=stadium, year=year, logo=logo)
        db.session.add(club)
        db.session.commit()
        flash('เพิ่มสโมสรเรียบร้อย', 'success')
        return redirect(url_for('clubs.all_clubs'))

    return render_template('clubs/new_club.html', title='New Club')

@clubs_bp.route('/search', methods=['POST'])
def search_clubs():
    club_name = request.form.get('club_name', '').strip()
    if club_name:
        clubs = db.session.query(Club).filter(Club.name.ilike(f'%{club_name}%')).all()
    else:
        clubs = db.session.query(Club).all()
    return render_template('clubs/search_club.html', clubs=clubs)

@clubs_bp.route('/<int:club_id>/info')
def club_info(club_id):
    club = Club.query.get_or_404(club_id)
    return render_template('clubs/info_club.html', title=club.name, club=club)

@clubs_bp.route('/<int:club_id>/update', methods=['GET', 'POST'])
def update_club(club_id):
    club = Club.query.get_or_404(club_id)

    if request.method == 'POST':
        club.name = request.form.get('name', club.name).strip()
        club.stadium = request.form.get('stadium', club.stadium).strip()
        year_raw = request.form.get('year', '').strip()
        club.logo = request.form.get('logo', club.logo).strip()

        if year_raw.isdigit():
            club.year = int(year_raw)

        db.session.commit()
        flash('อัปเดตสโมสรเรียบร้อย', 'success')
        return redirect(url_for('clubs.club_info', club_id=club.id))

    return render_template('clubs/update_club.html', title='Update Club', club=club)
