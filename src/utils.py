import os, json, base64


clear_cli = lambda: os.system('cls' if os.name == 'nt' else 'clear')

def load(file_path) -> list:
    """Return data"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, Exception):
        return []
    
def save(file_path, data):
    """Save data to file"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory): # Check directory
        os.makedirs(directory) # Create dirrectory if none
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving: {e}")

def encode_image(image_path=None, image=None):
    """
    Encode image to base64 from path or from image
    """
    if image_path:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    elif image:
            return base64.b64encode(image).decode('utf-8')