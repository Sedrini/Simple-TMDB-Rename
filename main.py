import requests
from bs4 import BeautifulSoup
import os
import PySimpleGUI as sg
from pathlib import Path

def paths():
    tmdb_folder = Path(os.environ["USERPROFILE"]) / "Documents" / "Simple TMDB Rename"
    if not os.path.exists(tmdb_folder):
        os.makedirs(tmdb_folder)

    return tmdb_folder
        
def escrape_write_txt(url):
    name_path = os.path.join(paths(), 'tmdb_scrape.txt')

    with open(name_path, 'w') as file:
        file.write('')
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text    
            soup = BeautifulSoup(html, 'html.parser')

            h3_tags = soup.find_all('h3')
            for h3_tag in h3_tags:
                a_tag = h3_tag.find('a')  
                if a_tag:
                    text = a_tag.text
                    if text != "← Back to season list":
                        with open(name_path, 'a') as file:
                            file.write(f'{text}\n')
        else:
            sg.popup("ERROR ",response.status_code)
    except ValueError:
        sg.popup("ERROR: INVALID URL ?")

def pre_rename_files(path_files, word_replace):
    path_txt = os.path.join(paths(), 'tmdb_scrape.txt')
    #Count lines of the txt
    with open(path_txt, 'r') as file:
        line_count = sum(1 for line in file)
    #check len files and words in txt are the same
    if len(os.listdir(path_files)) == line_count:
        rename_files(path_files, path_txt, word_replace)
    else:
        sg.popup(f"The folder has: {len(os.listdir(path_files))} words\nAnd the txt file has: {line_count} words")
    

def rename_files(path_files,path_txt,word_replace):
    with open(path_txt, "r") as f:
        nombres_episodios = [line.strip() for line in f.readlines()]
    archivos = os.listdir(path_files)
    for i in range(len(archivos)):
        viejo_nombre = os.path.join(path_files, archivos[i])
        nuevo_nombre = nombres_episodios[i] + os.path.splitext(archivos[i])[1]
        renovado = viejo_nombre.replace(word_replace, nuevo_nombre)
        os.rename(viejo_nombre, renovado)

def main_gui():
    #Buttons Pad
    buttons_pad = ((5, 0), (30, 0))
    default_pad2 = ((20, 0), (10, 0))
    #Go back button
    back_button = sg.Button('Go back',key='-BACK-',visible=False)


    sg.theme('DarkAmber')   

    # Rename Files LAYOUT
    layout2 = [  
        [sg.FolderBrowse("FOLDER",key="-FOLDER-",pad=buttons_pad),sg.Text(pad=buttons_pad)],
        [sg.Text('Word to replace',pad=buttons_pad),sg.Input(pad=buttons_pad,key='-WORD_REPLACE-')],
        [sg.Button('Rename',key='-RENAME_TMDB-',pad=((0, 0), (10, 0))),]]

    #TMDB SCRAPE LAYOUT
    layout1 = [  
        [sg.Text('TMDB URL'),sg.Input(key="-URL-")],
        [sg.Button('Scrape',key='-SCRAPE-')]]
    
    #MENU (buttons)
    layout0 = [
        [sg.Button('Scrape TMDB', font=('Helvetica', 13),pad=buttons_pad, key="-TMDB-")],
        [sg.Button('Replace Word', font=('Helvetica', 13),pad=buttons_pad, key="-REPLACE-")],
    ]
    
    #MENU LAYOUT
    layout = [[back_button,sg.Push(),sg.Text('TMDB Rename 1.0',justification='Middle', font=('Helvetica', 13),pad=((0, 0), (10, 0))),sg.Push()],
        [sg.Column(layout0, key='-MENU-',visible=True),sg.Column(layout1, key='-TMDB1-',visible=False),sg.Column(layout2, key='-RENAM1-',visible=False)]
        ]

    window = sg.Window('Simple TMDB Rename', layout,size=(500,300))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        elif event == "-TMDB-":
            window[f'-MENU-'].update(visible=False)
            window[f'-TMDB1-'].update(visible=True)
            back_button.update(visible=True)
        elif event == "-REPLACE-":
            window[f'-MENU-'].update(visible=False)
            window[f'-RENAM1-'].update(visible=True)
            back_button.update(visible=True)
        elif event == "-BACK-":
            window[f'-TMDB1-'].update(visible=False)
            window[f'-RENAM1-'].update(visible=False)
            window[f'-MENU-'].update(visible=True)
            back_button.update(visible=False)
        elif event == "-SCRAPE-":
            if values['-URL-'] == "":
                sg.popup('Must enter a URL ')
            else:
                escrape_write_txt(values['-URL-'])
        elif event == "-RENAME_TMDB-":
            if values['-FOLDER-'] == "":
                sg.popup('Must select a folder before ')
            elif not values['-WORD_REPLACE-'] or len(values['-WORD_REPLACE-'].strip()) <= 0:
                sg.popup('Must enter the word is going to be replaced')
            else:
                pre_rename_files(values['-FOLDER-'],values['-WORD_REPLACE-'] )

    window.close()

main_gui()