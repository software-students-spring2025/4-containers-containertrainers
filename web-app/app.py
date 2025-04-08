from flask import Flask, render_template, request, jsonify
import os
import glob 

app = Flask(__name__)

#does this work? 
RECORDINGS_FOLDER = '/app/recordings'
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)

#look for the next file, file numbers are sequential 
def get_next_file_number():
    """this gets the next file number"""
    existing_files = glob.glob(os.path.join(RECORDINGS_FOLDER, "recording_*webm"))
    #if no recordings 
    if not existing_files: 
        return 1
    numbers = []
    for filename in existing_files: 
        try:
            base = os.path.basename(filename)
            num_str = base.split('_')[1].split('.')[0]
            numbers.append(int(num_str))
        except (IndexError, ValueError):
            continue 

    return max(numbers) + 1 if numbers else 1

#main page 
@app.route('/')
def index():
    ''' flask render the main page'''
    return render_template('index.html')

#uploads to the volume 
@app.route('/upload', methods=['POST'])
def upload_audio():
    '''see if the file is in the resquest get the file into the volume'''
    if 'audio' not in request.files:
        return jsonify({'success': False})
    
    audio_file = request.files['audio']

    next_number = get_next_file_number()

    filename = f"recording_{next_number}.webm"

    filepath = os.path.join(RECORDINGS_FOLDER, filename)
    audio_file.save(filepath)

    return jsonify({'success':True, 'filename': filename})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)

 