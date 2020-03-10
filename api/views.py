from django.shortcuts import render
import dns.resolver as resolver
from django.shortcuts import HttpResponse
import json


def getdomain(request):
    sub = request.GET.get('sub')
    domain = request.GET.get('domain')
    target = sub+"."+domain
    try:
        result = resolver.Resolver().query(target).response.answer
        ls = []
        for i in result:
            for j in i.items:
                ls.append(j.to_text())
        res = dict()
        res['status'] = 1 if len(ls) > 0 else 0
        res['domain'] = target
        res['ip'] = ls
        return HttpResponse(json.dumps(res),content_type="application/json")

    except Exception as e:
        return HttpResponse("{'status':0}")


