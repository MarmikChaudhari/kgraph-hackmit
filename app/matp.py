import io
import base64
from flask import send_file, current_app
import matplotlib.pyplot as plt
import numpy as np

@current_app.route('/get-matplotlib-image')
def get_matplotlib_image():
    # Create a simple plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y)
    plt.title('Sample Matplotlib Plot')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    
    # Save the plot to a BytesIO object
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    
    # Encode the image to base64
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    # Clear the current figure
    plt.close()
    
    return img_str