import json
import re
import time
import uuid
import shortuuid
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import pymongo
import pymysql


class Data:

    def __init__(self, request):
        self.header = request.META
        self.request = request.data

    params = {}

    def sub(self, matched):
        var = matched.group(0)
        var = var[2:len(var) - 1]
        swicher = {
            int: lambda p: str(p),
            float: lambda p: str(p),
            str: lambda p: f'"{p}"',
            dict: lambda p: json.dumps(p),
            list: lambda p: json.dumps(p),
            tuple: lambda p: json.dumps(p)
        }
        if var in self.params:
            return swicher.get(type(self.params[var]))(self.params[var])
        raise Exception(f'参数 {var} 不存在')

    def analysis(self, matched):
        var = matched.group(0)
        var = var[2:len(var) - 1]
        swicher = {
            int: lambda p: str(p),
            float: lambda p: str(p),
            str: lambda p: p,
            dict: lambda p: json.dumps(p),
            list: lambda p: json.dumps(p),
            tuple: lambda p: json.dumps(p)
        }
        if var in self.params:
            return swicher.get(type(self.params[var]))(self.params[var])
        raise Exception(f'参数 {var} 不存在')

    def get_header(self, p):
        return self.header.get(p)

    def get_request(self, p):
        return self.request.get(p)

    def get_function(self, p):
        swicher = {
            "time": lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "uuid": lambda: str(uuid.uuid4()),
            "suuid": lambda: shortuuid.uuid(),
        }
        return swicher.get(p)()

    def var(self, obj):
        for i in obj['vars']:
            swicher = {
                "function": lambda p: self.get_function(p),
                "header": lambda p: self.get_header('HTTP_' + p.upper()),
                "request": lambda p: self.get_request(p),
                "string": lambda p: p,
                "int": lambda p: int(p),
                "float": lambda p: float(p),
                "array": lambda p: json.loads(p),
                "json": lambda p: json.loads(p),
                "null": lambda p: None
            }
            if result := swicher.get(i['type'])(i['value']) or i['default_type'] == 'null':
                self.params[i['key']] = result
            elif i['default_type'] == 'error':
                raise Exception(i['type'] + ' 类型数据 ' + i['key'] + ' 不存在')
            else:
                self.params[i['key']] = result

    def mysql(self, obj):
        try:
            sql_str = obj['sql']
            sql = re.sub(r'\$\{.*?\}', self.analysis, sql_str, count=0, flags=0)
            if obj['data_type'] == 'json':
                db = pymysql.connect("39.99.214.102", obj['db']['username'], obj['db']['password'],
                                     obj['db']['dbname'], cursorclass=pymysql.cursors.DictCursor)
            else:
                db = pymysql.connect("39.99.214.102", obj['db']['username'], obj['db']['password'],
                                     obj['db']['dbname'])
            cursor = db.cursor()
            dbname = obj['db']['dbname']
            cursor.execute(f"USE {dbname}")
            cursor.execute(sql)
            data = cursor.fetchall()
            db.close()
            if obj.get('var'):
                self.params.update({obj['var']: data})
        except Exception as ex:
            return str(ex)

    def mongo(self, obj):
        try:
            server = '39.99.214.102'
            mongo_dbname = obj['db']['dbname']
            mongo_username = obj['db']['username']
            mongo_password = obj['db']['password']
            mongo = f"mongodb://{mongo_username}:{mongo_password}@{server}:27017/{mongo_dbname}"
            conn = pymongo.MongoClient(mongo)
            collection = re.sub(r'\$\{.*?\}', self.analysis, obj['collection'], count=0, flags=0)
            col = conn[mongo_dbname][collection]
            sql = json.loads(obj['sql'])
            data = getattr(col, obj['function'])(sql)
            if obj.get('var'):
                if type(data) == pymongo.cursor.Cursor:
                    result = []
                    for i in data:
                        i['_id'] = str(i['_id'])
                        result.append(i)
                    self.params.update({obj['var']: result})
                elif type(data) == dict:
                    data['_id'] = str(data['_id'])
                    self.params.update({obj['var']: data})
                else:
                    self.params.update({obj['var']: str(data)})
        except Exception as ex:
            return str(ex)

    def main(self, opera):
        for i in opera['opera_list']:
            swicher = {
                "var": self.var,
                "mysql": self.mysql,
                "mongo": self.mongo,
            }
            swicher.get(i['type'])(i)
        try:
            swicher = {
                "string": lambda p: p,
                "json": lambda p: json.loads(p)
            }
            s_str = str(opera['return']['data'])
            result = re.sub(r'\$\{.*?\}', self.sub, s_str, count=0, flags=0)
            result = swicher.get(opera['return']['type'])(result)
            return result
        except Exception as ex:
            return str(ex)


class RestapiView(APIView):
    server = '39.99.214.102'
    mongo_password = 'Aa12345.'
    mongo = f'mongodb://root:{mongo_password}@{server}:27017/'
    conn = pymongo.MongoClient(mongo)
    db = conn['restapi']

    def get(self, request, p1=None, p2=None, p3=None, p4=None, p5=None):
        url = f'/{p1}'
        if p2:
            url += f'/{p2}'
        if p3:
            url += f'/{p3}'
        if p4:
            url += f'/{p4}'
        if p5:
            url += f'/{p5}'
        id = request.META.get('HTTP_API')
        if not id:
            return HttpResponse('HEADER 中缺少 API 认证', status=500)
        opera = self.db['url'].find_one(
            {'$or': [{'url': url, 'method': request.method}, {'url': url + '/', 'method': request.method}]})
        if not opera:
            return HttpResponse(f'{request.path} not found!', status=404)
        res = Data(request).main(opera)
        if opera['return']['type'] == 'string':
            return HttpResponse(res)
        return JsonResponse(res, safe=False)

    def post(self, request, p1=None, p2=None, p3=None, p4=None, p5=None):
        return self.get(request, p1, p2, p3, p4, p5)

    def put(self, request, p1=None, p2=None, p3=None, p4=None, p5=None):
        return self.get(request, p1, p2, p3, p4, p5)

    def patch(self, request, p1=None, p2=None, p3=None, p4=None, p5=None):
        return self.get(request, p1, p2, p3, p4, p5)

    def delete(self, request, p1=None, p2=None, p3=None, p4=None, p5=None):
        return self.get(request, p1, p2, p3, p4, p5)
