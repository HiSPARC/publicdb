from django.http import HttpResponse
from numpy import linspace, sqrt, exp, pi
import json

def _create_data():
    x = linspace(-10, 10)
    
    # Normal distribution pdf
    mu, s = 0., 1.
    y = 1 / sqrt(2 * pi * s ** 2) * exp(-(x - mu) ** 2 / (2 * s ** 2))
    
    return [[(u, v) for u, v in zip(x, y)]]

def data(request):
    response = HttpResponse(json.dumps(_create_data()),
                            mimetype='application/json')
    return response

def data_cors(request):
    response = HttpResponse(json.dumps(_create_data()),
                            mimetype='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response
