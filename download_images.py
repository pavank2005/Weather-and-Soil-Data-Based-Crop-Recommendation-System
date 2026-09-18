import os
import urllib.request
import shutil
import ssl

folder_path = os.path.join("static", "images")

# 1. Security Bypass (Fixes SSL Errors)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 2. Browser Masquerade (Pretends to be Chrome)
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')]
urllib.request.install_opener(opener)

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# --- NEW RELIABLE IMAGE LINKS (Unsplash) ---
image_urls = {
    'default': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600',
    'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600',
    'maize': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=600',
    'chickpea': 'https://upload.wikimedia.org/wikipedia/commons/4/46/Chickpea.JPG',
    'kidneybeans': 'https://upload.wikimedia.org/wikipedia/commons/6/62/Red_Kidney_Beans.jpg',
    'pigeonpeas': 'https://upload.wikimedia.org/wikipedia/commons/5/5d/Pigeon_peas_in_a_spoon.jpg',
    'mothbeans': 'https://upload.wikimedia.org/wikipedia/commons/0/07/Vigna_aconitifolia_Seeds.jpg',
    'mungbean': 'https://upload.wikimedia.org/wikipedia/commons/a/ac/Mung_beans.jpg',
    'blackgram': 'https://upload.wikimedia.org/wikipedia/commons/8/86/Black_gram.jpg',
    'lentil': 'https://upload.wikimedia.org/wikipedia/commons/8/81/Red_Lentils.jpg',
    'pomegranate': 'https://images.unsplash.com/photo-1615486511484-92e172cc416d?w=600',
    'banana': 'https://images.unsplash.com/photo-1571771896612-924b24059328?w=600',
    'mango': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=600',
    'grapes': 'https://images.unsplash.com/photo-1537640538965-a4824821d134?w=600',
    'watermelon': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600',
    'muskmelon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Cantaloupes.jpg/640px-Cantaloupes.jpg',
    'apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600',
    'orange': 'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5a?w=600',
    'papaya': 'https://images.unsplash.com/photo-1617112848923-cc946ae1df48?w=600',
    'coconut': 'https://images.unsplash.com/photo-1544376798-89aa6b82c6cd?w=600',
    'cotton': 'https://images.unsplash.com/photo-1594488518063-23963e62f4b0?w=600',
    'jute': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Jute.JPG',
    'coffee': 'https://images.unsplash.com/photo-1552345373-c82668e1a6c4?w=600',
    
    # --- UPDATED LINKS FOR INDIAN CROPS ---
    'ragi': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Eleusine_coracana_Indien.jpg', 
    'wheat': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600', # Changed to Unsplash
    'mustard': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/Mustard_Field_Bangla.jpg',
    'sugarcane': 'https://images.unsplash.com/photo-1601633591444-245842c556b6?w=600', # Changed to Unsplash
    'groundnut': 'https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=600'  # Changed to Unsplash
}

print("⬇️ Starting Reliable Download...")

# 1. Get Default Image first (Critical)
default_path = os.path.join(folder_path, "default.jpg")
if not os.path.exists(default_path):
    try:
        urllib.request.urlretrieve(image_urls['default'], default_path)
        print("✅ Default image downloaded.")
    except:
        print("❌ Critical: Could not download default image.")

# 2. Download the rest
for name, url in image_urls.items():
    if name == 'default': continue
    
    filepath = os.path.join(folder_path, f"{name}.jpg")
    
    # Force delete the 0-byte or broken files from previous failed run
    if os.path.exists(filepath) and os.path.getsize(filepath) < 1000: 
        os.remove(filepath)

    if not os.path.exists(filepath):
        try:
            print(f"⏳ Downloading {name}...", end=" ")
            urllib.request.urlretrieve(url, filepath)
            print("✅")
        except Exception as e:
            print(f"⚠️ Failed: {name}. Using Default.")
            if os.path.exists(default_path):
                shutil.copy(default_path, filepath)
    else:
        print(f"⏩ {name} OK.")

print("\n🎉 Images Updated Successfully!")