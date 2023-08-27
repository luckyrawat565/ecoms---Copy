from .models import address

def has_filled_address(user):
    if user.is_authenticated:
        try:    
            
            if user.profile.address_filled:
                return True
        except address.DoesNotExist:
            return False
    else:
        return False