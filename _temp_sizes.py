import os
for p in ['_temp_ssml_no.mp3','_temp_ssml_yes.mp3']:
    try:
        print(p, os.path.getsize(p))
    except FileNotFoundError:
        print(p, 'MISSING')
