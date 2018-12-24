import requests
import json
from bs4 import BeautifulSoup
import shutil
import os
import logging

logging.basicConfig(filename='app.log', level=logging.WARNING, filemode='w', format='%(name)s - %(levelname)s - %(message)s')
backend_url = "https://api.aware.wiki/submit/face/"
skip_subjects = "Kidnappings and Missing Persons"
details = ""
#
for x in range(1, 1000):
    response = requests.get('https://api.fbi.gov/wanted/v1/list', params={
        'page': x
    })
    data = json.loads(response.content)
    if data['items'] is None or len(data['items']) == 0:
        print("Stop fetching data")
        break
    print("fetch data from page %s and total data is %s" % (x, len(data['items'])))
    for wanted_person in data['items']:
        try:
            if skip_subjects not in wanted_person['subjects']:
                ex_data = {"data": wanted_person['url']}
                if wanted_person['images'] is not None and len(wanted_person['images']) > 0:
                    images = wanted_person['images']
                    for image in images:
                        pic = image['large']
                        if wanted_person['description'] is not None:
                            details = BeautifulSoup(wanted_person['description'], 'lxml').get_text()
                        elif wanted_person['reward_text'] is not None:
                            details = BeautifulSoup(wanted_person['reward_text'], 'lxml').get_text()
                        else:
                            details = BeautifulSoup(wanted_person['details'], 'lxml').get_text()
                        data = {
                            'title':wanted_person['title'],
                            'description': details,
                            'data': json.dumps(ex_data),
                        }
                        r = requests.get(pic, stream=True)

                        if r.status_code == 200:
                            file_name = 'data/' + os.path.basename(pic) + '.png'
                            with open(file_name, 'wb') as f:
                                r.raw.decode_content = True
                                shutil.copyfileobj(r.raw, f)
                            files = {'face_file': open(file_name, 'rb')}
                            r = requests.post(backend_url, files=files, data=data)
                            logging.warning(wanted_person['url'])
                            logging.warning(r.text)
                            print('Running ', wanted_person['url'])
        except Exception as e:
            logging.warning(wanted_person)
            logging.warning(e)
            continue