from flask import Flask, jsonify, request, make_response
from test_dome import main_spider
import json
from flask_cors import CORS, cross_origin

# 实例化 flask 对象
app = Flask(__name__)

CORS(app)


@app.route('/pyapi/spider', methods=['POST', 'OPTIONS'])
@cross_origin(methods=['POST'])
# @cross_origin(origin='/pyapi/spider', methods=['POST', 'GET'])
def TEST():
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type')

    data = request.get_json(force=True)
    username = request.get_json()["video_id"]
    try:

        return jsonify({"message": "Success","data":main_spider([username])})
    except:
        return '检查爬虫'

    # 处理参数，例如存储到数据库或返回响应
    # if request.is_json:
    #     try:
    #         print(main_spider([data['video_id']]))
    #         return '200'
    #     except:
    #         return 'error'
    # else:
    #     return 'Parameters are not in JSON format.'


@app.route('/pyapi/test/', methods=['GET'])
def index():
    return '接口测试数据'


# 连接本地的域
if __name__ == '__main__':

    app.run(host='192.168.1.180', port=7800, debug=True)  # 如果端口被占用，可以修改port的值，保持4位数就可以了
