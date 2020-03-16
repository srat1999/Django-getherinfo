from django.shortcuts import render
import dns.resolver as resolver
from django.contrib import messages
from django.shortcuts import HttpResponse,render
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
import json
from .models import XZ_article,SW_article
import requests
import re
from lxml import etree
import datetime



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


def catcharticle(request):

    def getsw():
        r = requests.session()
        content = r.get("https://www.sec-wiki.com/news").text
        conlist = re.findall(r'.*">(.*)</a></td><td><a target=".*', content, re.M)
        hreflist = re.findall(r'.*class="links" href=\"((https|http)://.*?)\">.*', content, re.M)
        tmp_sw = SW_article.objects.all()[0:13]
        tmp_sw_title = [tmp_article.title for tmp_article in tmp_sw]
        tmp_sw_link = [tmp_article.href for tmp_article in tmp_sw]
        linklist = [hreflist[i] for i in range(len(hreflist)) if hreflist[i] not in tmp_sw_link]
        conlist = [conlist[i] for i in range(len(conlist)) if conlist[i] not in tmp_sw_title]
        return conlist, linklist

    def filter_data(datas, exclude=[]):  # 接受xpath-list，并过滤指定字符
        datas = [str(data).replace(" ", "").strip() for data in datas]
        datas = [data for data in datas if len(data)]
        if not len(exclude):
            return datas
        else:
            for key in exclude:
                datas = [str(data).replace(key, "").strip() for data in datas]
            datas = [data for data in datas if len(data)]
            return datas

    class Article:
        def __init__(self, title, href):
            self.title = title
            self.href = href

    def getxz():
        URL = "https://xz.aliyun.com"
        r = requests.session()
        articles = []
        myhtml = r.get(URL).text
        mytree = etree.HTML(myhtml)
        dates = mytree.xpath('//p[@class="topic-info"]/text()')
        dates = filter_data(dates, exclude=["/"])
        # print(dates)
        titles = mytree.xpath('//a[@class="topic-title"]/text()')
        titles = filter_data(titles)
        # print(titles)
        hrefs = mytree.xpath('//a[@class="topic-title"]/@href')
        hrefs = filter_data(hrefs)
        hrefs = [URL + href for href in hrefs]
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        index = 0
        for date in dates:
            if now_date == date:
                article = Article(titles[index], hrefs[index])
                index += 1
                articles.append(article)
            else:
                break
        # print(articles)
        return articles

    conlist,linklist = getsw()

    # 未增加回滚事务
    # 去重
    for i in range(len(conlist)):
        sw_article = SW_article(title=conlist[i], href=linklist[i])
        sw_article.save()

    articles = getxz()
    for article in articles:
        xz_article = XZ_article(title=article.title,href=article.href)
        xz_article.save()

    return render(request,"articles.html")


def getarticle(request):
    if request.method == 'GET':
        if request.GET.get('tp'):
            type = request.GET.get('tp')
        else:
            type = 'xz'
        if request.GET.get('page'):
            page = request.GET.get('page')
        else:
            page = 1
        if type == "xz":
            articles = list(XZ_article.objects.all())
            # 此处进行分页
            paginator = Paginator(articles,10)
            try:
                articles = paginator.page(page)
            except PageNotAnInteger:
                paginator.page(1)
            except InvalidPage:
                return HttpResponse("invaliade")
            ctx = dict()
            ctx['type'] = 'xz'
            ctx['articles'] = articles
            return render(request,"articles.html",ctx)

        elif type == "sw":
            articles = list(SW_article.objects.all())
            paginator = Paginator(articles, 10)
            try:
                articles = paginator.page(page)
            except PageNotAnInteger:
                paginator.page(1)
            except InvalidPage:
                return HttpResponse("invaliade")
            ctx = dict()
            ctx['type'] = 'sw'
            ctx['articles'] = articles
            return render(request, "articles.html", ctx)
    else:
        HttpResponse("invalide")


