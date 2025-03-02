
import streamlit as st  
import PIL.Image  
import google.generativeai as genai
import time
import cv2, numpy as np 

genai.configure(api_key=API_KEY)

 
st.set_page_config(page_title="Homecook Pro", layout="wide")  
 
def resize_image_cv2(_image, max_size=512):  
    img_array = np.array(_image)  # Convert PIL Image to NumPy array  
    h, w = img_array.shape[:2]  
    scale = max_size / max(h, w)  
    new_w, new_h = int(w * scale), int(h * scale)  
    resized_img = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_AREA)  
    return PIL.Image.fromarray(resized_img)  # Convert back to PIL Image  

 
def extract_ingredients_tools(_images):  
    model = genai.GenerativeModel(model_name='gemini-2.0-flash')
    response = model.generate_content(contents=[f'''Extract all ingredients and cooking tools from these images; 
                                                if no ingredients or tools are detected, you MUST print:
                                                No ingredients or tools detected. Please re-upload appropriate images.''']+_images, 
                                                generation_config={"temperature": 0})

    return response.text  
 
def generate_recipe(_ingredients_tools, diet_preference, cuisine):  
    model = genai.GenerativeModel(model_name='gemini-1.5-pro')
    response = model.generate_content(contents=[f'''Generate a list of recipes using the following ingredients and tools ONLY: {_ingredients_tools}\n       
                      and the following dietary preference: {diet_preference} as well as considering the preferred cuisine type: {cuisine}\n 
                        If diet preference and/or cuisine is not given, generate a recipe without those restrictions\n
                        Include clear and precise step-by-step instructions and nutiritional information(calories (in kcal), macros etc) too 
                        If no recipe can be generated under the given parameters, admit that you can't'''], generation_config={"temperature": 0.5})

    return response.text  
 
# Sidebar for inputs
st.sidebar.header("Upload & Preferences")
uploaded_files = st.sidebar.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

diet_options = ["None", "Halal", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Kosher"]
diet_preference = st.sidebar.selectbox("Diet Preference", diet_options)

cuisine = st.sidebar.text_input("Cuisine Type", placeholder="e.g., Italian, Thai, Mexican", max_chars=30)

done_button = st.sidebar.button("Done Uploading")

# Main content area
st.markdown("<h1 style='text-align: center;'>🍽️ HomeCook Pro: Personalized Recipe Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your generated recipe will appear below</p>", unsafe_allow_html=True)


if done_button and uploaded_files:  
    st.session_state.reupload = False  # Reset state  
    images = [resize_image_cv2(PIL.Image.open(file)) for file in uploaded_files]  
    with st.spinner("Extracting ingredients... 🧐"):  
        ingredients_tools = extract_ingredients_tools(images)  
 
    if ingredients_tools != "No ingredients or tools detected. Please re-upload appropriate images.":  
        with st.spinner("Generating recipe... 🍽️"):  
            recipe = generate_recipe(ingredients_tools, diet_preference, cuisine)  
        if recipe:  
            st.write(recipe)
              
        else:  
            st.write("No valid recipe found.")  
    else:  
        st.session_state.reupload = True  # Trigger reupload prompt  
        st.error("No ingredients or tools detected. Please re-upload appropriate images.")  
        time.sleep(10)  
        st.rerun()  # Rerun the script to prompt reupload
elif done_button and not uploaded_files:  
    st.error("Please upload images.")