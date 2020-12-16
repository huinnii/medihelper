from pymongo import MongoClient

from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify, request

from my_project.static import config

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.medihelper

import requests

headers = {
    'Authorization': 'KakaoAK ' + config.kakao_api_key
}


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search_pharmacy')
def ph():
    return render_template('pharmacy.html')


@app.route('/search_medicine')
def medic():
    return render_template('medicine.html')


# 의약품 상세정보 가져오기
@app.route('/detail&seq=<id>')
def get_detail(id):
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode, quote_plus, unquote

    service_key = unquote(config.dataset_api_key)

    url = 'http://apis.data.go.kr/1471057/MdcinPrductPrmisnInfoService/getMdcinPrductItem'

    queryParams = '?' + urlencode(
        {
            quote_plus('ServiceKey'): service_key,
            quote_plus('item_seq'): id,
            quote_plus('induty'): '의약품',
            quote_plus('spclty_pblc'): '전문의약품'
        })

    requests = Request(url + queryParams)
    requests.get_method = lambda: 'GET'
    response_body = urlopen(requests).read()
    res = response_body.decode('utf-8')

    xmlobj = BeautifulSoup(res, 'lxml-xml')

    rows = xmlobj.find('item')

    datas = []

    # 의약품 정보(고유번호, 품목명, 업체명, 성상, 원료성분, 저장방법, 유효기간) 가져오기
    item_seq = rows.select_one('ITEM_SEQ').text
    item_name = rows.select_one('ITEM_NAME').text
    entp_name = rows.select_one('ENTP_NAME').text

    chart = rows.select_one('CHART').text
    material_name = rows.select_one('MATERIAL_NAME').text
    storage_method = rows.select_one('STORAGE_METHOD').text
    valid_term = rows.select_one('VALID_TERM').text

    # 효능효과 / 용법용량 / 주의사항 가져오기
    ee = rows.select_one('EE_DOC_DATA')
    ud = rows.select_one('UD_DOC_DATA')
    nb = rows.select_one('NB_DOC_DATA')

    ee_doc = ee.select('ARTICLE')
    ud_doc = ud.select('ARTICLE')
    nb_doc = nb.select('ARTICLE')

    elen = len(ee_doc)
    ulen = len(ud_doc)
    nlen = len(nb_doc)

    ee_doc_data = ""
    ud_doc_data = ""
    nb_doc_data = ""

    for i in range(0, elen):
        if ee_doc_data != "":
            ee_doc_data += ' '
        ee_doc_data += ee_doc[i]['title']

        if ee_doc[i].text != "":
            ee_doc_data += ' ' + ee_doc[i].text.strip()

    # print(ee_doc_data)

    for i in range(0, ulen):
        if ud_doc_data != "":
            ud_doc_data += ' '
        ud_doc_data += ud_doc[i]['title']

        para = ud_doc[i].select('PARAGRAPH')

        for j in range(0, len(para)):
            if para[j]['tagName'] == 'p':
                ud_doc_data += ' ' + para[j].text.strip()

        # if ud_doc[i].text != "":
        #    ud_doc_data += ' ' + ud_doc[i].text.strip()

    # print(ud_doc_data)

    for i in range(0, nlen):
        if nb_doc_data != "":
            nb_doc_data += ' '
        nb_doc_data += nb_doc[i]['title']

        para = nb_doc[i].select('PARAGRAPH')

        for j in range(0, len(para)):
            if para[j]['tagName'] == 'p':
                nb_doc_data += ' ' + para[j].text.strip()

        # if nb_doc[i].text != "":
        #   nb_doc_data += ' ' + nb_doc[i].text.strip()

    # print(nb_doc_data)

    doc = {
        'item_seq': item_seq,
        'item_name': item_name,
        'entp_name': entp_name,
        'chart': chart,
        'material_name': material_name,
        'storage_method': storage_method,
        'valid_term': valid_term,
        'ee_doc_data': ee_doc_data,
        'ud_doc_data': ud_doc_data,
        'nb_doc_data': nb_doc_data
    }

    print(doc)

    return render_template('detail.html', data=doc)


perPage_list = 10


@app.route('/medicine', methods=['POST'])
def search_medicine():
    word = request.form['keyword']
    option = request.form['option']

    from urllib.request import Request, urlopen
    from urllib.parse import urlencode, quote_plus, unquote

    service_key = unquote(config.dataset_api_key)

    url = 'http://apis.data.go.kr/1471057/MdcinPrductPrmisnInfoService/getMdcinPrductItem'

    if option == '품목명':
        queryParams = '?' + urlencode(
            {
                quote_plus('ServiceKey'): service_key,
                quote_plus('item_name'): word,
                quote_plus('induty'): '의약품',
                quote_plus('spclty_pblc'): '전문의약품',
                quote_plus('pageNo'): '1',
                quote_plus('numOfRows'): perPage_list
            })

    if option == '업체명':
        queryParams = '?' + urlencode(
            {
                quote_plus('ServiceKey'): service_key,
                quote_plus('entp_name'): word,
                quote_plus('induty'): '의약품',
                quote_plus('spclty_pblc'): '전문의약품',
                quote_plus('pageNo'): '1',
                quote_plus('numOfRows'): perPage_list
            })

    requests = Request(url + queryParams)
    requests.get_method = lambda: 'GET'
    response_body = urlopen(requests).read()
    res = response_body.decode('utf-8')

    xmlobj = BeautifulSoup(res, 'lxml-xml')

    total = xmlobj.find('totalCount').text

    rows = xmlobj.findAll('item')

    rowsLen = len(rows)

    datas = []

    for data in range(0, rowsLen):
        # 의약품 정보(고유번호, 품목명, 업체명, 성상, 원료성분, 저장방법, 유효기간) 가져오기
        item_seq = rows[data].select_one('ITEM_SEQ').text
        item_name = rows[data].select_one('ITEM_NAME').text
        entp_name = rows[data].select_one('ENTP_NAME').text

        doc = {
            'item_seq': item_seq,
            'item_name': item_name,
            'entp_name': entp_name
        }

        datas.append(doc)

    print(datas)

    return jsonify({'result': 'success', 'data': datas, 'total': total})


@app.route('/medicine/page', methods=['POST'])
def get_medic_page():
    word = request.form['area']
    option = request.form['option']
    page = request.form['page']

    from urllib.request import Request, urlopen
    from urllib.parse import urlencode, quote_plus, unquote

    service_key = unquote(config.dataset_api_key)

    url = 'http://apis.data.go.kr/1471057/MdcinPrductPrmisnInfoService/getMdcinPrductItem'

    if option == '품목명':
        queryParams = '?' + urlencode(
            {
                quote_plus('ServiceKey'): service_key,
                quote_plus('item_name'): word,
                quote_plus('induty'): '의약품',
                quote_plus('spclty_pblc'): '전문의약품',
                quote_plus('pageNo'): page,
                quote_plus('numOfRows'): perPage_list
            })

    if option == '업체명':
        queryParams = '?' + urlencode(
            {
                quote_plus('ServiceKey'): service_key,
                quote_plus('entp_name'): word,
                quote_plus('induty'): '의약품',
                quote_plus('spclty_pblc'): '전문의약품',
                quote_plus('pageNo'): page,
                quote_plus('numOfRows'): perPage_list
            })

    requests = Request(url + queryParams)
    requests.get_method = lambda: 'GET'
    response_body = urlopen(requests).read()
    res = response_body.decode('utf-8')

    xmlobj = BeautifulSoup(res, 'lxml-xml')

    rows = xmlobj.findAll('item')

    rowsLen = len(rows)

    datas = []

    for data in range(0, rowsLen):
        # 의약품 정보(고유번호, 품목명, 업체명, 성상, 원료성분, 저장방법, 유효기간) 가져오기
        item_seq = rows[data].select_one('ITEM_SEQ').text
        item_name = rows[data].select_one('ITEM_NAME').text
        entp_name = rows[data].select_one('ENTP_NAME').text

        doc = {
            'item_seq': item_seq,
            'item_name': item_name,
            'entp_name': entp_name
        }

        datas.append(doc)

    return jsonify({'result': 'success', 'data': datas})


@app.route('/place', methods=['POST'])
def search_pharmacy():
    area = request.form['area']

    params = {
        'query': area
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/address.json', headers=headers, params=params)

    data2 = response.json()

    address = data2['documents'][0]['address']

    x = address['x']
    y = address['y']

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
            'size': perPage_list,
            'sort': "distance"
        }

        response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', headers=headers, params=params2)

        is_end = response.json()['meta']['is_end']

        if page == 1:
            data = response.json()['documents']

    total = page * perPage_list

    return jsonify({'result': 'success', 'total': total, 'data': data, 'x': x, 'y': y})


@app.route('/page', methods=['POST'])
def search_list():
    area = request.form['area']
    page = request.form['page']

    params = {
        'query': area
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/address.json', headers=headers, params=params)

    data2 = response.json()

    address = data2['documents'][0]['address']

    x = address['x']
    y = address['y']

    params2 = {
        'y': y,
        'x': x,
        'radius': '20000',
        'query': '약국',
        'page': page,
        'size': perPage_list,
        'sort': "distance"
    }

    response = requests.get('https://dapi.kakao.com/v2/local/search/keyword.json', headers=headers, params=params2)

    data = response.json()['documents']

    return jsonify({'result': 'success', 'data': data, 'x': x, 'y': y})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
