import requests, json, os, sqlite3, re, subprocess, sys
from moviepy import AudioFileClip
from dotenv import load_dotenv
from colorama import Fore, init

load_dotenv()
init(autoreset=True)

MS_DATA = os.getenv('ms_data')
MS_FOLDER = os.getenv('ms_folder')

con = sqlite3.connect(MS_DATA)
cur = con.cursor()

if len(sys.argv) < 2:
    lst_functions = ['', 'add to base', 'clean metadata']
    print(Fore.RED + 'Enter number of function!')
    [print(Fore.LIGHTYELLOW_EX + str(id), Fore.LIGHTGREEN_EX + '==>', Fore.LIGHTBLUE_EX +i) for id, i in enumerate(lst_functions) if i]
    sys.exit(1)

entry = int(sys.argv[1])


if entry == 1:
    counter = 0
    for i in os.listdir():
        if i.endswith('.mp30') or  i.endswith('.m4a') or i.endswith('.opus'):
            track = AudioFileClip(i)
            duration = track.duration
            if counter == 30:
                print(Fore.LIGHTGREEN_EX + 'done')
                con.commit()
                cur.close()
                con.close()
                exit()

            if 1200 > duration > 0:
                counter += 1
                sample = track.subclipped(1, duration//3).write_audiofile("sample.mp3", logger=None)
                
                try:
                    raw_data = subprocess.run(['songrec', 'recognize', 'sample.mp3', '--json'], capture_output=True, text=True)
                    fine_data = json.loads(raw_data.stdout)

                except requests.exceptions.JSONDecodeError as e:
                    print(Fore.LIGHTRED_EX + str(e))
                    con.commit()
                    cur.close()
                    con.close()
                    exit()

                reserved_names = [int(re.search(r'\d+',  n).group(0)) for n in os.listdir(MS_FOLDER) if re.search(r'\d+',  n)]
                
                genre = fine_data['track']['genres']['primary'].replace("'", '_')
                try: album = fine_data['track']['sections'][0]['metadata'][0]['text'].replace("'", '_')
                except IndexError: album = 'unkown'
                try: label = fine_data['track']['sections'][0]['metadata'][1]['text'].replace("'", '_')
                
                except IndexError: label = 'unkown'
                try: date = fine_data['track']['sections'][0]['metadata'][2]['text'].replace("'", '_')
                except IndexError: date = 'unkown'

                title = fine_data['track']['title'].replace("'", '_') 
                artist = fine_data['track']['subtitle'].replace("'", '_')
                
                subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', i, '-map_metadata', '-1', '-c:a', 'copy', 'output.opus'])
                
                os.rename('output.opus', MS_FOLDER + str(max(reserved_names) + 1) + '.opus')
                path = MS_FOLDER + str(max(reserved_names) + 1) + '.opus'

                cur.execute(f"""INSERT INTO items (
                                    id, 
                                    artist, 
                                    title, 
                                    album, 
                                    date, 
                                    label, 
                                    path,
                                    genre)                     

                                VALUES (
                                   {max(reserved_names) + 1}, 
                                   '{artist}',
                                   '{title}', 
                                   '{album}', 
                                   '{date}', 
                                   '{label}', 
                                   '{path}', 
                                   '{genre}')
                           """)
                
                subprocess.run(['sudo', 'rm', i])
         
elif entry == 2: 
    print("No need!!!")
    exit()
    for i in os.listdir(MS_FOLDER):
        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', MS_FOLDER+i, '-map_metadata', '-1', '-c:a', 'copy', MS_FOLDER + 'cleaned' + i])
        subprocess.run(['rm', MS_FOLDER+i])
       
con.commit()
cur.close()
con.close()
