import config
import random, string
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

USER_DB_DIR = config.USER_DB_DIR
DATABASE_URI = config.DATABASE_URI
# USER_DB_DIR = 'fake'
# DATABASE_URI = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000'

client = MongoClient(DATABASE_URI)
db = client['hw6']
users = db['users']

def gen_session_token(length=24):
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(length)])
    return token

class User:
    username = ''
    password = ''
    token = ''

    def __init__(self, _id):
        user = users.find_one({'_id': _id})
        self.cur = user
        self._id = _id
        self.username = user['username']
        self.password = user['password']
        self.token = user['token']
        self.imageURL = user['imageURL']

    def __str__(self):
        return self.username

    @classmethod
    def filter(cls, *args, **kwargs):
        query = []
        for user in users.find(kwargs):
            query.append(User(user['_id']))
        return query

    @classmethod
    def create(cls, username, password, token=None, imageURL='/images/user-default-img.jpg'):
        id = users.insert_one({
                'username': username, 
                'password': generate_password_hash(password),
                'token': token,
                'imageURL': imageURL
            }).inserted_id
        user = cls(id)
        return user

    def is_existed(self):
        return User.filter(username=self.username) != []

    def delete(self):
        return users.delete_one({'_id': self._id})
    
    def save(self):
        users.update_one(
            {'_id':self._id}, 
            {
                '$set' : {
                    'username': self.username,
                    'password': self.password,
                    'token': self.token,
                    'imageURL': self.imageURL
                }
            },
            upsert=True
        )

    def authenticate(self, password):
        return check_password_hash(self.password, password)

    def edit_pwd(self, password):
        self.password = generate_password_hash(password)
        self.terminate_session()

    def init_session(self):
        self.token = gen_session_token()
        self.save()
        return self.token

    def terminate_session(self):
        self.token = None
        self.save()
                
if __name__ == '__main__':
    # user1 = User.filter(name='hoang')[0]
    
    # print(user1.delete())
    print(User.filter())