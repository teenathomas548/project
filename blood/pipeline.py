# auth_pipeline.py

from .models import DonorProfile

def create_donor_profile(backend, user, response, request, *args, **kwargs):
    if not hasattr(user, 'donorprofile'):  # Check if DonorProfile already exists
        # Create a new DonorProfile for this user
        DonorProfile.objects.create(
            user=user,
            # Set additional fields if they are available from Google response data
            blood_type=response.get('blood_group', ''),
            contact_number=response.get('phone_number', ''),
            # Add more fields as needed
        )
    
    # Set donor_id in the session
    request.session['donor_id'] = user.donorprofile.id
