from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

from my_project.static import config

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search_pharmacy')
def ph():
    return render_template('pharmacy.html')


import requests

headers = {
    'Authorization': 'KakaoAK ' + config.api_key
}

@app.route('/place', methods=['POST'])
def search_pharmacy():
    area = request.form['area']

    print(area)

    params = {
        'query': area
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/address.json', headers=headers, params=params)

    # print(response.text,params)
    # print(response.status_code)

    data2 = response.json()

    address = data2['documents'][0]['address']

    x = address['x']
    y = address['y']

    print(x,y)

    is_end = False
    page = 0

    while is_end == False:
        page += 1

        params2 = {
            'y': y,
            'x': x,
            'radius': '20000',
            'query': '약국',
            'page': page,
            'sort': "distance"
        }

        response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', headers=headers, params=params2)

        is_end = response.json()['meta']['is_end']

        if page == 1:
            data = response.json()['documents']
        # print(is_end)

    total = page * 15

    return jsonify({'result': 'success', 'total': total, 'data': data, 'x': x, 'y': y})


@app.route('/page', methods=['POST'])
def search_list():
    area = request.form['area']

    params = {
        'query': area
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/address.json', headers=headers, params=params)

    # print(response.text,params)
    # print(response.status_code)

    data2 = response.json()

    address = data2['documents'][0]['address']

    x = address['x']
    y = address['y']

    page=request.form['page']

    print(page)

    params2 = {
        'y': y,
        'x': x,
        'radius': '20000',
        'query': '약국',
        'page': page,
        'sort': "distance"
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', headers=headers, params=params2)

    data = response.json()['documents']

    return jsonify({'result': 'success','data': data, 'x': x, 'y': y})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
