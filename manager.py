import pyperclip, requests, os, re, tqdm, shelve

def is_url(url):
    return url.startswith('https') or url.startswith('http')

def get_url_from_clipboard():
    print("Parsing URL From Clipboard...")
    url = pyperclip.paste()
    if is_url(url):
        return url
    else:
        print("URL Must Start With http Or Https")
        exit()

def check_filename():
    print("Do You Wanna Continue Downloading File ? (Y/N)...")
    if input().lower().startswith('y'):
        filename    = input('So Please Enter The Downloaded File')

        if os.path.isfile(filename):
            filesize    = os.path.getsize(filename)
            return {'Range'  : f"{filesize}-", 'filename' : filename}
        else:
            print("Can't Find Any File With This Name...")
            exit()
    else:
        return {}

def is_downloadable_link(headers):
    if 'text' in headers or 'html' in headers:
        raise "Can't Find Any File In This URL"

def get_filename(url, r_headers):
    if 'filename' not in r_headers:
        filename    = os.path.basename(url)
        filename_re = re.compile(r"(.*)(\.)(.*)")
        match_obj   = filename_re.search(filename)
        i           = 1
        while os.path.isfile(filename):
            filename    = f"{match_obj.groups()[0]}({i}){match_obj.groups()[1]}{match_obj.groups()[2]}"
            i           += 1

    else:
        filename    = r_headers['filename']

    return filename

def check_if_url_exists(filename):
    with shelve.open('urls') as data:
        return data.get(filename)

def add_link(filename, url):
    with shelve.open('urls') as data:
        data[filename]  = url

def download_file(url, r_headers):
    if not is_url(url):
        url     = check_if_url_exists(url)

    try:
        print("Start Downloading The File...")
        res         = requests.get(url, stream=True, headers=r_headers)
    except Exception as ex:
        print('Error ' + str(ex))
        exit()

    filesize    = res.headers.get('content-length')
    is_downloadable_link(headers=res.headers)
    filename    = get_filename(url, r_headers)
    add_link(filename, url)
    print(f"FileName : {filename} & FileSize : {filesize}")

    if 'filename' in r_headers:
        print("Continue Downloading...")
        with open(r_headers['filename'], "ab") as f:
            pbar    = tqdm.tqdm(total=float(filesize), unit='iB', unit_scale=True, desc=filename)
            for chunk in res.iter_content(10000):
                f.write(chunk)
                pbar.update(len(chunk))

    else:
        print("Creating File...")
        with open(filename, "wb") as f:
            pbar    = tqdm.tqdm(total=float(filesize), unit='iB', unit_scale=True, desc=filename)
            for chunk in res.iter_content(10000):
                f.write(chunk)
                pbar.update(len(chunk))

    print("Finish !")

url     = get_url_from_clipboard()
headers = check_filename()
download_file(url, headers)