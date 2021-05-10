import psycopg2
import cv2
import os
from config import Config
from typing import Dict


############################################
from detect_missing_people import FaceRecog
############################################

PATH = '../media/'

class VideoCheck:
    def __init__(self) -> None:
        self.conn = self.connect()

    def connect(self) -> object:
        conn = None
        try:
            params = Config()

            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)
            
            cur = conn.cursor()

            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            db_version = cur.fetchone()
            print(db_version)

            return conn

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            
        finally:
            if conn is not None:
                print('Database connected successfully.')
    
    def disconnect(self) -> None:
        self.conn.close()
    
    def fetch_all_missing_people_data(self) -> Dict[str, tuple]:
        global PATH
        cur = self.conn.cursor()
        cur.execute("SELECT * from listings_listing")
        records = cur.fetchall()

        missing_people = {}
        missing_people_state = {}

        for record in records:
            _id = record[0]
            name = record[1]
            image_path = record[6]
            requestor_id = record[12]
            is_found = record[13]

            if is_found:
                continue

            missing_people[_id] = (name, PATH + image_path, requestor_id)
            missing_people_state[_id] = is_found

        return missing_people, missing_people_state


def save_images(images: Dict[int, tuple] ) -> None:
    global PATH
    PATH += '/taken_photos/'
    for _id, images_info in images.items():
        for image, date in images_info:
            date = PATH + date[:10] + '/'
            os.makedirs(date, exist_ok=True)
            print(date + str(_id) + '.jpg')
            cv2.imwrite(date + str(_id) + '.jpg', image)    


if __name__ == '__main__':
    video_check = VideoCheck()
    
    missing_people_data, missing_people_state = video_check.fetch_all_missing_people_data()

    face = FaceRecog(missing_people_state)

    missing_people_images_from_videos = face.start_face_recog(missing_people_data, show=False)
    print(missing_people_data, missing_people_state, missing_people_images_from_videos)
    save_images(missing_people_images_from_videos)

    video_check.disconnect()

