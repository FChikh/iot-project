import re

def translate_room_id(room_id):
    # Use regex to insert a space between the letters and numbers
    transformed_id = re.sub(r'([A-Za-z]+)(\d+)', r'\1 \2', room_id)
    
    # Insert a dot before the last three digits
    transformed_id = re.sub(r'(\d{1,3})(\d{3})$', r'\1.\2', transformed_id)
    
    return transformed_id



