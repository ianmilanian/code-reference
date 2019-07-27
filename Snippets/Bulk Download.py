import requests
from tqdm import tqdm
from multiprocessing import Pool

def download_images(urls):
    def get_image(url):
        try:
            r = session.get(url, stream=True, verify=False)
        except: return False
        path = url.split("/")[-1]
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        return True
    session = requests.Session()
    session.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) Chrome/59.0.3071.109"}
    requests.packages.urllib3.disable_warnings()  # turn off SSL warnings
    return [url for url in tqdm(urls) if get_image(url)]

def bulk_download(urls):
    def chunk(l,n):
        return [l[i:i+n] for i in range(0,len(l),n)]
    with Pool() as p:
        failed = p.map(download_images, chunk(urls, 1000))
        print(failed)

if __name__ == "__main__":
    urls = [
        'http://example.org/test0.jpg',
        'http://example.org/test1.jpg',
        'http://example.org/test2.jpg',
        'http://example.org/test3.jpg',
        'http://example.org/test4.jpg',
        'http://example.org/test5.jpg',
        'http://example.org/test6.jpg',
        'http://example.org/test7.jpg',
        'http://example.org/test8.jpg',
        'http://example.org/test9.jpg']
    bulk_download(urls)
