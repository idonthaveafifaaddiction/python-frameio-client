import requests
import math
import concurrent.futures
import threading
import time

thread_local = threading.local()

class FrameioUploader(object):
  def __init__(self, asset, file):
    self.asset = asset
    self.file = file

  def _read_chunk(self, file, size):
    while True:
      data = file.read(size)
      if not data:
        break
      yield data

  def _get_session(self):
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

  def _upload_chunk(self, task):
    url = task[0]
    chunk = task[1]
    order = task[2]

    if order == 0:
      print("Sleeping for 30 seconds")
      time.sleep(30)
      print("Done sleeping")

    session = self._get_session()

    session.put(url, data=chunk, headers={
      'content-type': self.asset['filetype'],
      'x-amz-acl': 'private'
    })

    print(f"Completed uploading chunk {order}")

  def upload(self):
    total_size = self.asset['filesize']
    upload_urls = self.asset['upload_urls']
    size = int(math.ceil(total_size / len(upload_urls)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
      for i, chunk in enumerate(self._read_chunk(self.file, size)):
        # if i == 0:
        #   task = (upload_urls[i], chunk, i)
        #   executor.submit(self._upload_chunk, task)
        #   time.sleep(10)
        # else:
        #   task = (upload_urls[i], chunk, i)
        #   executor.submit(self._upload_chunk, task)
        
        task = (upload_urls[i], chunk, i)
        executor.submit(self._upload_chunk, task)
