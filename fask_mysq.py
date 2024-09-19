from flask import Flask, request
import pymysql

app = Flask(__name__)


@app.route('/greet', methods=['GET'])
def greet():
    db = pymysql.connect(host="192.168.1.80", port=3306, user="remo80", password="juzhun2023", database="zt")

    author_url_list = []
    cursor = db.cursor()
    author_data_url = "SELECT author_uid,author_url FROM `zt_author` WHERE author_uid!='' and author_url!=''"
    cursor.execute(author_data_url)
    author_url = cursor.fetchall()
    for author in author_url:
        author_url_list.append(author)
    cursor.close()
    db.close()
    return author_url_list



if __name__ == '__main__':
    app.run(debug=True)