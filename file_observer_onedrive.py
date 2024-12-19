import os
from dotenv import load_dotenv
import schedule
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

changed_files = []
folder_to_watch = "./slides/pptx/"

def sync_folder():
    global changed_files
    print('Reseted changed files variable.')
    changed_files = []
    os.system(f'rclone sync OneDrive:/slides/pptx {folder_to_watch}')
    print('This files changed: ')
    print(changed_files)
    if (changed_files): build_pdf()


def build_pdf():
    print('Building PDFs...')
    for file in changed_files:
        os.system(f'unoconvert {file}.pptx {file.replace("pptx", "pdf")}.pdf')
    print("Uploading PDFs...")
    os.system(f'rclone sync ./slides/pdf OneDrive:/slides/pdf')
    

class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global changed_files
        # print(event.src_path)
        file_path = event.src_path.split(".pptx")
        if len(file_path) > 1:
            if file_path[0] not in changed_files:
                changed_files.append(file_path[0])

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


schedule.every(10).seconds.do(sync_folder)

if __name__ == "__main__":
    monitor_folder(folder_to_watch)
