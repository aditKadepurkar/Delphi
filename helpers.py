import os
import subprocess
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID


def find_window(app_name):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for window in windows:
        # print(window)
        # if 'kCGWindowName' in window and 'kCGWindowOwnerName' in window:
            # print(window['kCGWindowOwnerName'])
        if window['kCGWindowOwnerName'] == app_name:
            return window
    return None

# Resize the window
def resize_window(window, x_bound, y_bound, width, height):
    # Get the window ID and current bounds
    # window_id = window['kCGWindowNumber']
    # bounds = window['kCGWindowBounds']
    
    # New position and size
    new_position = (x_bound, y_bound)
    new_size = (width, height)
    
    # Use an AppleScript command to resize the window
    script = f"""
    tell application "System Events"
        set the position of window 1 of process "{window["kCGWindowOwnerName"]}" to {{{new_position[0]}, {new_position[1]}}}
        set the size of window 1 of process "{window["kCGWindowOwnerName"]}" to {{{new_size[0]}, {new_size[1]}}}
    end tell
    """
    try:
        subprocess.run(['osascript', '-e', script])
        return "Success"
    except Exception as e:
        return e

def list_files(initdir: str, file_extensions: list):
    '''
    Returns a list of file under initdir and all its subdirectories
    that have file extension contained in file_extensions.
    ''' 
    file_list = []
    file_count = {key: 0 for key in file_extensions}  # for reporting only
    
    # Traverse through directories to find files with specified extensions
    for root, _, files in os.walk(initdir):
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in file_extensions:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
                # increment type of file
                file_count[ext] += 1
    
    # total = len(file_list)
    # print(f'There are {total} files under dir {initdir}.')
    # for k, n in file_count.items():
        # print(f'   {n} : ".{k}" files')
    return file_list
