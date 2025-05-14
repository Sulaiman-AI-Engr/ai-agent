import json
from datetime import datetime
from urllib.parse import urlparse
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import Business, Customer, Interaction, Message, Booking
from forms import LoginForm, RegistrationForm, ProfileForm, PasswordChangeForm, ChatbotForm
from utils import get_interaction_stats, get_booking_stats, get_customer_stats, format_duration

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        business = Business.query.filter_by(email=form.email.data).first()
        if business and business.check_password(form.password.data):
            login_user(business)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        business = Business(
            business_name=form.business_name.data,
            email=form.email.data,
            business_type=form.business_type.data,
            phone=form.phone.data,
            address=form.address.data
        )
        business.set_password(form.password.data)
        
        db.session.add(business)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    interaction_stats = get_interaction_stats(current_user.id)
    booking_stats = get_booking_stats(current_user.id)
    customer_stats = get_customer_stats(current_user.id)
    
    # Get recent interactions
    recent_interactions = Interaction.query.filter_by(business_id=current_user.id).order_by(Interaction.start_time.desc()).limit(5).all()
    
    # Get upcoming bookings
    upcoming_bookings = Booking.query.filter(
        Booking.business_id == current_user.id,
        Booking.booking_time > datetime.utcnow(),
        Booking.status == 'scheduled'
    ).order_by(Booking.booking_time).limit(5).all()
    
    return render_template(
        'dashboard/index.html',
        interaction_stats=interaction_stats,
        booking_stats=booking_stats,
        customer_stats=customer_stats,
        recent_interactions=recent_interactions,
        upcoming_bookings=upcoming_bookings,
        format_duration=format_duration
    )


@app.route('/dashboard/interactions')
@login_required
def interactions():
    interactions = Interaction.query.filter_by(business_id=current_user.id).order_by(Interaction.start_time.desc()).all()
    return render_template('dashboard/interactions.html', interactions=interactions, format_duration=format_duration)


@app.route('/dashboard/interaction/<int:interaction_id>')
@login_required
def interaction_detail(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    
    # Security check - ensure the interaction belongs to the current business
    if interaction.business_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('interactions'))
    
    messages = Message.query.filter_by(interaction_id=interaction.id).order_by(Message.timestamp).all()
    
    return render_template('dashboard/interaction_detail.html', interaction=interaction, messages=messages)


@app.route('/dashboard/bookings')
@login_required
def bookings():
    bookings = Booking.query.filter_by(business_id=current_user.id).order_by(Booking.booking_time.desc()).all()
    return render_template('dashboard/bookings.html', bookings=bookings)


@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.business_name.data = current_user.business_name
        form.business_type.data = current_user.business_type
        form.phone.data = current_user.phone
        form.address.data = current_user.address
    
    if form.validate_on_submit():
        current_user.business_name = form.business_name.data
        current_user.business_type = form.business_type.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    password_form = PasswordChangeForm()
    
    return render_template('dashboard/profile.html', form=form, password_form=password_form)


@app.route('/dashboard/change-password', methods=['POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    
    return redirect(url_for('profile'))


@app.route('/dashboard/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    form = ChatbotForm()
    
    return render_template('dashboard/chatbot.html', form=form)


@app.route('/api/charts/interactions')
@login_required
def api_interactions_chart():
    interaction_stats = get_interaction_stats(current_user.id)
    return jsonify(interaction_stats)


@app.route('/api/charts/bookings')
@login_required
def api_bookings_chart():
    booking_stats = get_booking_stats(current_user.id)
    return jsonify(booking_stats)


@app.route('/api/charts/customer-types')
@login_required
def api_customer_types_chart():
    customer_stats = get_customer_stats(current_user.id)
    return jsonify(customer_stats)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message='Server error'), 500