# Reference:
# https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url

import ctypes
import os
import requests
import shutil
import zipfile


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def unzip_patch(hearthstone_dir):
    with zipfile.ZipFile(os.path.join(hearthstone_dir, 'temp.zip'), 'r') as zipped_patch:
        zipped_patch.extractall(hearthstone_dir)


def patch(hearthstone_dir):
    source = os.path.join(hearthstone_dir, 'patch')
    destination = hearthstone_dir

    # Taken from
    # https://stackoverflow.com/questions/7419665/python-move-and-overwrite-files-and-folders
    for src_dir, dirs, files in os.walk(source):
        dst_dir = src_dir.replace(source, destination, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def cleanup(hearthstone_dir):
    os.remove(hearthstone_dir + '\\temp.zip')
    shutil.rmtree(hearthstone_dir + '\\patch')


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("Some Title")

    hearthstone_dir = "C:\\Program Files (x86)\\Hearthstone"

    while not os.path.exists(hearthstone_dir):
        print("Your Hearthstone installation could not be located.")
        print("Please enter the path where you have Hearthstone installed: ")
        hearthstone_dir = input()

    print(f"Patch will be installed to {hearthstone_dir}")
    print("Downloading patch, please wait...")

    try:
        file_id = '1L6K6tVsXpFtPxUSgLTpxtNXVfN24Ym4l'
        destination = hearthstone_dir + '\\temp.zip'
        download_file_from_google_drive(file_id, destination)
    except BaseException:
        print("Patch Download Error: could not download patch.")
        print("Here are some potential causes:")
        print("1. There may be something in your network that is interfering with the download.")
        print("2. Google Drive may have limited download hits on the patch. Where the patch is stored online will need to be revisited by the HearthstoneAccess development team.")

    print("Patching Hearthstone, please wait...")
    try:
        unzip_patch(hearthstone_dir)
        patch(hearthstone_dir)
        print("Successfully patched!")
    except BaseException:
        print("Could not patch your game. Please ask leibylucw.")

    try:
        cleanup(hearthstone_dir)
    except BaseException:
        print("Could not remove temporary files.")

    print("Press enter to exit the patcher.")
    input()
