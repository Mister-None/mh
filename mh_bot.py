import requests, json, os, sqlite3, re, subprocess, sys
from moviepy import AudioFileClip
from dotenv import load_dotenv
from colorama import Fore, init
import time
load_dotenv()
init(autoreset=True)

MS_DATA = os.getenv('ms_data')
MS_FOLDER = os.getenv('ms_folder')

con = sqlite3.connect(MS_DATA)
cur = con.cursor()
def sub(raw):
    raw = re.sub(r"""[,.()"'|!?/«»_:;”=’`~\n“]""", ' ', raw)
    raw = re.sub(r'[\[\]]', ' ', raw)
    raw = re.sub(' +', '_', raw)
    raw = re.sub(r'^_', '', raw)
    raw = re.sub(r'_$', '', raw)
    return raw.lower().strip() 

if len(sys.argv) < 2:
    lst_functions = ['', 'add to base', 'clean metadata', 'play by arist', 'normalize', 'remove duplicactes']
    print(Fore.RED + 'Enter number of function!')
    [print(Fore.LIGHTYELLOW_EX + str(id), Fore.LIGHTGREEN_EX + '==>', Fore.LIGHTBLUE_EX +i) for id, i in enumerate(lst_functions) if i]
    sys.exit(1)

entry = int(sys.argv[1])

if entry == 0:
    for i in os.listdir(MS_FOLDER):
        files = [i[0] for i in cur.execute(f"select id from items where concat(id,'.opus') = '{i}'")]
        if not files:
            print(i)

elif entry == 1:
    counter = 0
    for i in os.listdir():
        if i.endswith('.mp3') or  i.endswith('.m4a') or i.endswith('.opus'):
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
                    time.sleep(5)
                except requests.exceptions.JSONDecodeError as e:
                    print(Fore.LIGHTRED_EX + str(e))
                    con.commit()
                    cur.close()
                    con.close()
                    exit()

                reserved_names = [int(re.search(r'\d+',  n).group(0)) for n in os.listdir(MS_FOLDER) if re.search(r'\d+',  n)]
                
                try:
                    genre = fine_data['track']['genres']['primary']
                    genre = sub(genre)
                except KeyError: genre ='unkown'
                try: album = fine_data['track']['sections'][0]['metadata'][0]['text'].replace("'", '_')
                except IndexError: album = 'unkown'
                try: label = fine_data['track']['sections'][0]['metadata'][1]['text'].replace("'", '_')
                
                except IndexError: label = 'unkown'
                try: date = fine_data['track']['sections'][0]['metadata'][2]['text'].replace("'", '_')
                except IndexError: date = 'unkown'

                title = fine_data['track']['title']
                title = sub(title)
                artist = fine_data['track']['subtitle']
                artist = sub(artist)
                
                music_data = [i[0] for i in cur.execute("select concat(artist, ' ', title) from items where artist !='unkown' and title !='unkown'")]

                if str(artist + ' ' +  title) not in music_data:
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
                else: 
                    print(Fore.LIGHTGREEN_EX + str(artist + ' ' +  title), 'in database!!!')
                subprocess.run(['sudo', 'rm', i])
                subprocess.run(['rm', 'sample.mp3'])
         
elif entry == 2: 
    print("No need!!!")
    exit()
    for i in os.listdir(MS_FOLDER):
        subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', MS_FOLDER+i, '-map_metadata', '-1', '-c:a', 'copy', MS_FOLDER + 'cleaned' + i])
        subprocess.run(['rm', MS_FOLDER+i])

elif entry == 3:
    artists = [i[0] for i in cur.execute('SELECT artist, count(artist) from items group by artist having count(artist) > 1 order by 1 DESC')]
    print(*artists,  sep='\n')
    entry = input('>>> ').split(' ')
    if len(entry) == 1:
        entry = f"('{entry[0]}')"
    else:
        for id, i in enumerate(entry):
            entry[id] = f'{i}'
        entry = tuple(entry)
    playlist = [i[0] for i in cur.execute(f"SELECT path from items where  artist in {entry} order by random()")]
    subprocess.run(['mpv'] + playlist)

elif entry == 4:
    raw_data = [i for i in cur.execute(f"SELECT artist, title from items")]
    for x, y in raw_data:
        new_x = sub(x)
        new_y = sub(y)
        cur.execute(f"update items set artist='{new_x}',  title='{new_y}' where artist='{x}' and title='{y}'")

elif entry == 5:
    raw_data = [i[0] for i in cur.execute("select concat(artist, ' ', title), count(concat(artist, ' ', title)) from items where artist !='unkown' and title !='unkown' group by concat(artist, ' ', title) having count(concat(artist, ' ', title)) > 1")]
    for i in raw_data:
        duplicates = [i[0] for i in cur.execute(f"select id from items where concat(artist, ' ', title)='{i}'")]
        remained = min(duplicates) 
        for j in duplicates:
            if j != remained:
                file = [i[0] for i in cur.execute(f"select path from items where id={j}")][0]

                cur.execute(f"delete from items where id={j}")
                subprocess.run(['rm', file])

con.commit()
cur.close()
con.close()
