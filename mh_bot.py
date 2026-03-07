import requests,  json, os,  sqlite3, re, dotenv
from moviepy import AudioFileClip
"ffmpeg -i input.opus -map_metadata -1 -c:a copy output.opus"
data = {
    'api_token': '',
    'return': '',}

f1 = 'Music'
#files = {'file': open('sample.mp3', 'rb')}
#raw_result = requests.post('https://api.audd.io/', data=data, files=files).json()
#print(raw_result)
#exit()
con = sqlite3.connect('ms_data/ms.db')
cur = con.cursor()
counter = 0
for i in os.listdir(f1):
    f2 = os.path.join(f1, i)
    for j  in os.listdir(f2):
        f3 = os.path.join(f2, j)
        if os.path.isdir(f3):
            for k in os.listdir(f3):
                f4 = os.path.join(f3, k)
                if f4.endswith('.opus'):


                    track = AudioFileClip(f4)
                    duration = track.duration
                    if counter == 30:
                        con.commit()
                        cur.close()
                        con.close()
                        exit()
                    if 1200 > duration > 0:
                        #os.system(f"ffmpeg -i {f4} -c:a libopus -b:a 128k {f3}/output.opus")
                        #os.system(f"rm {f4}")
                        #f4 = f3 + '/output.opus'
                        counter += 1
                        sample = track.subclipped(1, duration//2).write_audiofile("sample.mp3")
                        files = {'file': open('sample.mp3', 'rb')}
                        try:
                            raw_result = requests.post('https://api.audd.io/', data=data, files=files).json()
                        except requests.exceptions.JSONDecodeError:
                            con.commit()
                            cur.close()
                            con.close()
                            exit()

                        reserved_names = [int(re.search(r'\d+',  n).group(0)) for n in os.listdir('ms_data') if re.search(r'\d+',  n)]
                        if raw_result['status'] == "success" and raw_result['result']:
                            result = raw_result['result']
                            entry = 'y'
                            if entry == 'n':
                                con.commit()
                                cur.close()
                                con.close()
                                exit()
                            elif entry == 'y':
                                try:
                                    os.rename(f"{f4}", 'ms_data/' + str(max(reserved_names) + 1) + '.opus')
                                except FileNotFoundError:
                                    con.commit()
                                    cur.close()
                                    con.close()
                                    exit()


                                path = '/home/m/ms_data/' + str(max(reserved_names) + 1) + '.opus'
                                cur.execute(f"""INSERT INTO items (
                                            id, 
                                            artist, 
                                            title, 
                                            album, 
                                            release_date, 
                                            label, 
                                            path,
                                            tag)

                                        VALUES (
                                            {max(reserved_names) + 1}, 
                                            ?, 
                                            ?, 
                                            ?, 
                                            ?, 
                                            ?, 
                                            '{path}', 
                                            '{j}')
                                            """, 
                                            [
                                                result.get('artist', 'unkown'),
                                                result.get('title', 'unkown'),
                                                result.get('album', 'unkown'),
                                                result.get('release_date', 'unkown'),
                                                result.get('label', 'unknown')
                                            ])

                        elif raw_result['status'] == "success": 
                            os.rename(f"{f4}", 'ms_data/' + str(max(reserved_names) + 1) + '.opus')
                            path = '/home/m/ms_data/' + str(max(reserved_names) + 1) + '.opus'
                            cur.execute(f"""INSERT INTO items (
                                        id, 
                                        artist, 
                                        title, 
                                        album, 
                                        release_date, 
                                        label, 
                                        path,
                                        tag)

                                    VALUES (
                                        {max(reserved_names) + 1}, 
                                        'unkown', 
                                        'unkown', 
                                        'unkown', 
                                        'unkown', 
                                        'unkown', 
                                        '{path}', 
                                        '{j}')""")
                        else:
                            print(raw_result)
                            con.commit()
                            cur.close()
                            con.close()
                            exit()
        else: pass
#            f4 = f3
#            if f4.endswith('.opus'):
#                track = AudioFileClip(f4)
#                duration = track.duration
#                if 600 > duration > 0:
#                    sample = track.subclipped(1, duration//2).write_audiofile("sample.mp3")
#                    files = {'file': open('sample.mp3', 'rb')}
#                    raw_result = requests.post('https://api.audd.io/', data=data, files=files).json()
#                    reserved_names = [int(re.search(r'\d+',  n).group(0)) for n in os.listdir('ms_data') if re.search(r'\d+',  n)]
#                    if raw_result['status'] == "success" and raw_result['result']:
#                        result = raw_result['result']
#                        entry = 'y'
#                        if entry == 'n':
#                            con.commit()
#                            cur.close()
#                            con.close()
#                            exit()
#                        elif entry == 'y':
#                            os.rename(f4, 'ms_data/' + str(max(reserved_names) + 1) + '.opus')
#                            path = '/home/m/ms_data/' + str(max(reserved_names) + 1) + '.opus'
#                            cur.execute(f"""INSERT INTO items (
#                                        id, 
#                                        artist, 
#                                        title, 
#                                        album, 
#                                        release_date, 
#                                        label, 
#                                        path,
#                                        tag)
#
#                                    VALUES (
#                                        {max(reserved_names) + 1}, 
#                                        ?, 
#                                        ?, 
#                                        ?, 
#                                        ?, 
#                                        ?, 
#                                        '{path}', 
#                                        '{i}')
#                                        """, 
#                                        [
#                                            result.get('artist', 'unkown'),
#                                            result.get('title', 'unkown'),
#                                            result.get('album', 'unkown'),
#                                            result.get('release_date', 'unkown'),
#                                            result.get('label', 'unknown')
#                                        ])
#
#                    else: 
#                        os.rename(f4, 'ms_data/' + str(max(reserved_names) + 1) + '.opus')
#                        path = '/home/m/ms_data/' + str(max(reserved_names) + 1) + '.opus'
#                        cur.execute(f"""INSERT INTO items (
#                                    id, 
#                                    artist, 
#                                    title, 
#                                    album, 
#                                    release_date, 
#                                    label, 
#                                    path,
#                                    tag)
#
#                                VALUES (
#                                    {max(reserved_names) + 1}, 
#                                    'unkown', 
#                                    'unkown', 
#                                    'unkown', 
#                                    'unkown', 
#                                    'unkown', 
#                                    '{path}', 
#                                    '{i}')""")

                    #

#
#for j in info:
#    print(j)
#sqlite3 ms_data/ms.db "insert into items (id, artist, title, album, release_date, label, path, tag) values (2, 'Агата Кристи', 'Опиум для никого', 'Избранное', '2008-01-01', 'Первое музыкальное Издательство', '/home/m/ms_data/2.opus', 'rus_rock')" 

con.commit()
cur.close()
con.close()
