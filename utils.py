from datetime import datetime, timedelta
from models import Interaction, Booking, Customer

def get_interaction_stats(business_id):
    """Get interaction statistics for a business"""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    week_start = now - timedelta(days=now.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0)
    month_start = datetime(now.year, now.month, 1, 0, 0, 0)
    
    # Get counts for different time periods
    today_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.start_time >= today_start
    ).count()
    
    week_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.start_time >= week_start
    ).count()
    
    month_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.start_time >= month_start
    ).count()
    
    total_count = Interaction.query.filter(
        Interaction.business_id == business_id
    ).count()
    
    # Get daily interactions for the last 7 days
    daily_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        count = Interaction.query.filter(
            Interaction.business_id == business_id,
            Interaction.start_time >= day_start,
            Interaction.start_time <= day_end
        ).count()
        
        daily_data.append({
            'day': day.strftime('%a'),
            'count': count
        })
    
    # Get interaction types distribution
    chat_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.interaction_type == 'chat'
    ).count()
    
    call_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.interaction_type == 'call'
    ).count()
    
    message_count = Interaction.query.filter(
        Interaction.business_id == business_id,
        Interaction.interaction_type == 'message'
    ).count()
    
    return {
        'today': today_count,
        'week': week_count,
        'month': month_count,
        'total': total_count,
        'daily_data': daily_data,
        'types_data': [
            {'type': 'Chat', 'count': chat_count},
            {'type': 'Call', 'count': call_count},
            {'type': 'Message', 'count': message_count}
        ]
    }

def get_booking_stats(business_id):
    """Get booking statistics for a business"""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    week_start = now - timedelta(days=now.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0)
    month_start = datetime(now.year, now.month, 1, 0, 0, 0)
    
    # Upcoming bookings
    upcoming_bookings = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.booking_time > now,
        Booking.status == 'scheduled'
    ).count()
    
    # Today's bookings
    today_bookings = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.booking_time >= today_start,
        Booking.booking_time < today_start + timedelta(days=1)
    ).count()
    
    # This week's bookings
    week_bookings = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.booking_time >= week_start,
        Booking.booking_time < week_start + timedelta(days=7)
    ).count()
    
    # Get daily bookings for the next 7 days
    daily_data = []
    for i in range(0, 7):
        day = now + timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        count = Booking.query.filter(
            Booking.business_id == business_id,
            Booking.booking_time >= day_start,
            Booking.booking_time <= day_end
        ).count()
        
        daily_data.append({
            'day': day.strftime('%a'),
            'count': count
        })
    
    # Get booking status distribution
    scheduled_count = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.status == 'scheduled'
    ).count()
    
    completed_count = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.status == 'completed'
    ).count()
    
    cancelled_count = Booking.query.filter(
        Booking.business_id == business_id,
        Booking.status == 'cancelled'
    ).count()
    
    return {
        'upcoming': upcoming_bookings,
        'today': today_bookings,
        'week': week_bookings,
        'daily_data': daily_data,
        'status_data': [
            {'status': 'Scheduled', 'count': scheduled_count},
            {'status': 'Completed', 'count': completed_count},
            {'status': 'Cancelled', 'count': cancelled_count}
        ]
    }

def get_customer_stats(business_id):
    """Get customer statistics for a business"""
    # Get all customers who have interactions or bookings with this business
    customer_ids = set()
    
    interactions = Interaction.query.filter_by(business_id=business_id).all()
    for interaction in interactions:
        customer_ids.add(interaction.customer_id)
    
    bookings = Booking.query.filter_by(business_id=business_id).all()
    for booking in bookings:
        customer_ids.add(booking.customer_id)
    
    # Count total unique customers
    total_customers = len(customer_ids)
    
    # Count new vs returning customers
    new_customers = Customer.query.filter(
        Customer.id.in_(customer_ids),
        Customer.is_new == True
    ).count()
    
    returning_customers = total_customers - new_customers
    
    return {
        'total': total_customers,
        'new': new_customers,
        'returning': returning_customers,
        'type_data': [
            {'type': 'New', 'count': new_customers},
            {'type': 'Returning', 'count': returning_customers}
        ]
    }

def format_duration(seconds):
    """Format seconds into a human-readable duration"""
    if not seconds:
        return "0s"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    result = []
    if hours:
        result.append(f"{hours}h")
    if minutes:
        result.append(f"{minutes}m")
    if seconds and not hours:
        result.append(f"{seconds}s")
    
    return " ".join(result)