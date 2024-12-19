import os
from dotenv import load_dotenv
import schedule
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

changed_files = []
folder_to_watch = "slides"

def sync_folder():
    global changed_files
    print('Reseted changed files variable.')
    changed_files = []
    os.system('nextcloudcmd --path /teste_slides/pptx ./slides/ https://' + os.getenv('NEXTLCLOUD_USER') + ':' + os.getenv('NEXTCLOUD_PASSWORD') + '@nextcloud.lasseufpa.org')
    print('This files changed: ')
    print(changed_files)
    if (changed_files): build_pdf()


def build_pdf():
    print('Building PDFs...')
    for file in changed_files:
        os.system(f'unoconvert {file} {file.replace(folder_to_watch, "pdfs").replace(".pptx", ".pdf")}')
    

class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global changed_files
        file_path = event.src_path.split("~")[0]
        if file_path.endswith('.pptx'):

            if event.src_path not in changed_files:
                changed_files.append(event.src_path)

        if file_path.endswith('.pptx.'):            
            real_path = file_path.split('/.')[0]
            real_name = file_path.split('/.')[1].split('.pptx')[0]
            real_file = real_path + '/' + real_name + '.pptx'

            if real_file not in changed_files:
                changed_files.append(real_file)

def monitor_folder(folder_path):
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    print(f"Monitoring folder: {folder_path}")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


schedule.every(1).minutes.do(sync_folder)

if __name__ == "__main__":
    monitor_folder(folder_to_watch)
