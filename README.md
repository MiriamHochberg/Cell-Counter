# Cell Counter

A tool for counting cells in microscope images, built for Dr. Anya Alayev's biology research 
lab at Yeshiva University's Stern College, which studies the combined and individual effects 
of different drugs on triple-negative breast cancer cells.

Counting cells by hand from microscope images is slow, so this app does the counting 
automatically — then lets you click to fix any mistakes for an exact count.

## In Action Pictures 
**Before** — raw microscope image  
<img width="1280" height="720" alt="Slide3" src="https://github.com/user-attachments/assets/0d03c887-2aaf-4a95-92ba-0391918d410b" />

**After** — automatically detected and circled cells  
<img width="1023" height="646" alt="Screenshot 2026-06-30 at 3 54 31 PM" src="https://github.com/user-attachments/assets/34b0ec48-7b3c-462b-ad50-f7afb5aae3d0" />

**Before** — raw microscope image  
<img width="1280" height="720" alt="Slide40" src="https://github.com/user-attachments/assets/2add1f9c-67f8-4df0-9c37-949d194671b9" />


**After** — automatically detected and circled cells  
<img width="1022" height="654" alt="Screenshot 2026-06-30 at 3 57 46 PM" src="https://github.com/user-attachments/assets/031526ae-782b-4d94-9516-0a194c90cef5" />


## Impact
Manual counting on dense images can take 1-3 minutes per image. This tool reduces that to 
roughly 30-45 seconds, including time spent reviewing and correcting the automated count — an 
average time reduction of about 78% on dense images.

## How It Works
1. Upload a `.jpg` microscope image
2. The app automatically detects and circles each cell
3. Click any circle to remove it, or click empty space to add one, to correct any mistakes
4. Save the final image and cell count to the `results/` folder
5. Click "Upload another image" to go back to the home screen

## A Note on Accuracy
Manual and automated counts won't always match exactly — even careful manual counting can vary 
between counters when cells are dim, overlapping, or ambiguous. This tool isn't meant to replace 
human judgment, but to drastically cut down the time needed to get a reliable count, with manual 
review built in to catch any errors.

## Built With
- Python, tkinter (GUI), PIL/Pillow (image display and saving), NumPy and SciPy (image 
  processing and cell detection)
- Built with the assistance of Claude (Anthropic) for implementing the image processing and 
  detection logic

## How to Run
Requires Python 3.

Install the required libraries:
`pip3 install pillow numpy scipy`

Make sure `cell_main.py` and `cell_detect.py` are in the same folder, then run:
`python3 cell_main.py`
