import streamlit as st
import cv2
import numpy as np
from utils.image_processor import process_image, detect_room_features
from utils.layout_generator import generate_layout_suggestions
from utils.visualization import create_layout_visualization
import io
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Interior Design Assistant",
    page_icon="🏠",
    layout="wide"
)

def main():
    st.title("Interior Design Assistant 🏠")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Room Details")
        
        # Room dimensions
        length = st.number_input("Room Length (meters)", min_value=1.0, max_value=20.0, value=5.0)
        width = st.number_input("Room Width (meters)", min_value=1.0, max_value=20.0, value=4.0)
        height = st.number_input("Room Height (meters)", min_value=1.0, max_value=5.0, value=2.5)
        
        # Room type selection
        room_type = st.selectbox(
            "Room Type",
            ["Living Room", "Bedroom", "Home Office", "Dining Room", "Kitchen"]
        )
        
        # Style preferences
        style = st.selectbox(
            "Preferred Style",
            ["Modern", "Traditional", "Minimalist", "Scandinavian", "Industrial"]
        )
        
        # Budget range
        budget = st.slider("Budget Range ($)", 1000, 10000, (2000, 5000))

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Room Photo")
        uploaded_file = st.file_uploader("Choose a photo of your room", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Room", use_column_width=True)
            
            # Process image
            img_array = np.array(image)
            features = detect_room_features(img_array)
            
            # Show processing status
            with st.spinner("Processing room features..."):
                processed_features = process_image(img_array)
                st.success("Room analysis complete!")

    with col2:
        if uploaded_file:
            st.subheader("Layout Suggestions")
            
            # Generate layout suggestions
            suggestions = generate_layout_suggestions(
                length, width, height,
                room_type,
                style,
                budget,
                processed_features
            )
            
            # Display visualization
            visualization = create_layout_visualization(
                length, width,
                suggestions,
                room_type
            )
            st.pyplot(visualization)
            
            # Display recommendations
            st.subheader("Design Recommendations")
            for idx, suggestion in enumerate(suggestions['recommendations'], 1):
                with st.expander(f"Suggestion {idx}"):
                    st.write(suggestion['description'])
                    st.write(f"Estimated Cost: ${suggestion['cost']}")
                    st.write("Key Features:")
                    for feature in suggestion['features']:
                        st.write(f"- {feature}")

if __name__ == "__main__":
    main()
