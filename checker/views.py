from django.shortcuts import render
from urllib.parse import urlparse
import requests as r
import re
import pickle
import pandas as pd
from bs4 import BeautifulSoup
import os
import xmltodict
import datetime
from .models import PhisWebsite
# Create your views here.


def check_right_click_disabled(content):
    check = re.search('event.button == 2', content) or re.search(
        '<body oncontextmenu="return false" onselectstart="return false" ondragstart="return false">', content)
    if check is not None:
        return -1
    else:
        return 1


def get_age_of_domain(url):
    whois_url = "https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=at_6hReptiQp1sIX8es8bPO8ihgkskd4&domainName="+url
    rq = r.get(whois_url)
    res = xmltodict.parse(rq.text)

    try:
        domain_registered_at = res['WhoisRecord']['createdDate'].split("-")
        domain_registered_at.pop()
        no_of_months = (datetime.date.today().year - int(domain_registered_at[0])) * 12 + (
            datetime.date.today().month - int(domain_registered_at[1]))
        print(no_of_months)
        if no_of_months > 6:

            return 1
        else:
            return -1
    except Exception as e:
        return -1


def check_url(url):
    check_url_len = len(url)

    if check_url_len < 54:
        URL_LENGTH = 1
    elif check_url_len >= 54:
        URL_LENGTH = -1
        At_Symbol = -1
    if url.find("@") == -1:
        At_Symbol = 1
    Hyphen_Symbol = -1
    if url.find("-") == -1:
        Hyphen_Symbol = 1
    try:
        position = url.index("//")
    except ValueError:
        double_slash_redirecting = -1
    if position+1 > 7:
        double_slash_redirecting = -1
    else:
        double_slash_redirecting = 1
    headers = {'API-OPR': 'oowk884so80s08w88wwcsc0w0cok4go8kgc04cg8 '}
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    page_rank_url = 'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D=' + domain
    rq = r.get(page_rank_url, headers=headers)
    res = rq.json()
    page_rank = res['response'][0]['page_rank_decimal']

    if page_rank < 4:
        Page_Rank = -1
    else:
        Page_Rank = 1
    Google_index = -1
    google_search = "https://www.google.com/search?q=site:" + domain + "&hl=en"
    res = r.get(google_search, cookies={'CONSENT': "YES+1"})
    soup = BeautifulSoup(res.content, "html.parser")
    not_index = re.compile("did not match any documents")
    if soup(text=not_index):
        Google_index = -1
    else:
        Google_index = 1
    domain_name = urlparse(url).netloc

    page = r.get(url)

    soup = BeautifulSoup(page.text, features='lxml')
    fav_icon = soup.find("link", rel="shortcut icon")

    if fav_icon is None:
        fav_icon = soup.find("link", rel="icon")

    if fav_icon and domain_name in fav_icon:
        Favicon = 1
    else:
        Favicon = -1
    images = soup.find_all("img")

    if domain_name not in images:
        Request_URL = -1
    else:
        Request_URL = 1
      # Web traffic and phistank
    age_of_domain = get_age_of_domain(url)

    return [URL_LENGTH, At_Symbol, double_slash_redirecting, Hyphen_Symbol, age_of_domain, Favicon, Request_URL, Page_Rank, Google_index]


def check(request):
    if request.method == "POST":
        url = request.POST['check_url']

        if PhisWebsite.objects.filter(site_name=url).first():
            return render(request, "home.html", context={"url": url, "type": "Phising", "message": "The following url might be a phising site. Please do not visit the following site and report it to authorities."})
        else:

            URL_Length, At_Symbol, double_slash_redirecting, Hyphen_Symbol, age_of_domain, Favicon, Request_URL, Page_Rank, Google_index = check_url(
                url)
            print(URL_Length, At_Symbol, double_slash_redirecting,
                  Hyphen_Symbol, age_of_domain, Favicon, Request_URL, Page_Rank, Google_index)
            X_pred = pd.DataFrame({'URL_Length': [URL_Length], 'having_At_Symbol': [At_Symbol], 'double_slash_redirecting': [
                double_slash_redirecting], 'HavingHyphen': [Hyphen_Symbol], "age_of_domain": [age_of_domain], "Favicon": [Favicon], 'Request_URL': Request_URL, 'Page_Rank': [Page_Rank], 'Google_Index': [Google_index]})

            with open("model.pkl", 'rb') as file:
                model = pickle.load(file)
            y = model.predict(X_pred)
            print(y)
            if y == -1:
                PhisWebsite.objects.create(site_name=url, url_length=URL_Length, having_at=At_Symbol, double_slash_redirecting=double_slash_redirecting,
                                           HavingHyphen=Hyphen_Symbol, age_of_domain=age_of_domain, Favicon=Favicon, Request_URL=Request_URL, Page_Rank=Page_Rank, Google_Index=Google_index)
                return render(request, "home.html", context={"url": url, "type": "Phising", "message": "The following url might be a phising site. Please do not visit the following site and report it to authorities."})

            else:
                return render(request, "home.html", context={"url": url, "type": "Normal", "message": "The following url is safe to visit."})
        return render(request, "home.html")
