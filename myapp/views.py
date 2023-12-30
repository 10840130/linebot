from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
#from myapp.models import*

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, AudioSendMessage, VideoSendMessage, TemplateSendMessage
from linebot.models import ButtonsTemplate, MessageTemplateAction, URITemplateAction, PostbackTemplateAction, PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn
from linebot.models import ImagemapSendMessage, MessageImagemapAction, URIImagemapAction, BaseSize, ImagemapArea
from linebot.models import DatetimePickerTemplateAction
from linebot.models import BubbleContainer, ImageComponent, BoxComponent, TextComponent, IconComponent,ButtonComponent, SeparatorComponent, FlexSendMessage, URIAction
from urllib.parse import parse_qsl
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

import requests


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


'''
sendflex中的圖片位置因放在static中記得調整ngrok虛擬伺服器連結!
輸入關鍵字要調整
sendQuickreply為興趣類型項目快素選單(可選動作片、劇情片、恐怖片、喜劇片、動畫片、愛情片)
sendCarousel是電影轉盤(本周新片、上映中、即將上映各三部)

'''

@csrf_exempt
#12行標識函式式可以被跨域訪問
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            if isinstance(event, MessageEvent):
                mtext = event.message.text
                if mtext =='哈囉':
                    sendText(event)
                elif mtext == '本週電影':
                    scrape(event)
                elif mtext == '本周電影':
                    scrape(event)
                elif mtext =='推薦電影':
                    sendQuickreply(event)
                elif mtext =='電影':
                    sendCarousel(event)
                elif mtext =='看電影':
                    sendCarousel(event)
                elif mtext =='現正熱映電影':
                    sendPopular(event)
                elif mtext =='動作片':
                    sendActionMovie(event)
                elif mtext =='恐怖片':
                    sendHorror(event)
                elif mtext =='家庭片':
                    sendFamily(event)
                elif mtext =='戰爭片':
                    sendWar(event)
                elif mtext =='紀錄片':
                    sendDocumentary(event)
                elif mtext =='冒險片':
                    sendAdventure(event)
                elif mtext =='科幻片':
                    sendSciencefiction(event)
                elif mtext =='奇幻片':
                    sendFantasy(event)
                elif mtext =='犯罪片':
                    sendCrime(event)
                elif mtext =='懸疑片':
                    sendSuspense(event)
                word = '#'
                if word in mtext:
                    movie_search(event,mtext)
                else:
                
                    line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(text=event.message.text))

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def sendText(event):  #傳送文字
        try:
            message=TextSendMessage(text="你好，我是Moviebot")
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="傳送文字發生錯誤！"))

def scrape(event):
    try:
        response = requests.get(
            "https://movies.yahoo.com.tw/movie_thisweek.html")
            
        html = BeautifulSoup(response.text, "html.parser")


        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='本週電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='本週電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))


def movie_search(event,mtext):
    try:
        mtext=mtext.replace('#', '')
        response = requests.get(
            'https://movies.yahoo.com.tw/moviesearch_result.html?keyword='+mtext) #網址組合
            
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"},limit=3)
        foto_contents = html.find_all("div", {"class":"release_foto"},limit=3)
    
        message = TemplateSendMessage(alt_text='電影搜尋',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img").get("src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            #enName = info_item.find("div", {"class": "en"}).a.text.strip()
            #intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            #intro = intro[:40] + '...'
            #movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")
            timer = info_item.find("div", {"class": "time"}).text.strip()
            intro_url = info_item.find("a", {"class": "btn_s_introduction"}).get("href")

            # 容器


        
            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{timer}",
                actions=[
                    URITemplateAction(
                        label='影片大綱',
                        uri=f"{intro_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='電影搜尋', template=carousel_template)
                        
        
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))


        
        
def sendQuickreply(event):
    try:
        message = TextSendMessage(
            text = '您對哪種類型電影感興趣?',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="動作片",text="動作片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="恐怖片",text="恐怖片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="家庭片",text="家庭片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="戰爭片",text="戰爭片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="懸疑片",text="懸疑片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="冒險片",text="冒險片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="科幻片",text="科幻片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="奇幻片",text="奇幻片")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="犯罪片",text="犯罪片")
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤'))
        
def sendCarousel(event):
    try:
        message = TemplateSendMessage(
            alt_text='本週新片',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/April2023/A0fPKGtRZxCWLqlUF8LV-1080x1539.jpg',
                            title='本週新片',
                            text='新片上映',
                            actions=[
                                URITemplateAction(
                                    label='豪門心計',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E8%B1%AA%E9%96%80%E5%BF%83%E8%A8%88-the-origin-of-evil-14950'
                                ),
                                URITemplateAction(
                                    label='烈火浩劫',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E7%83%88%E7%81%AB%E6%B5%A9%E5%8A%AB-the-blaze-15028'
                                ),
                                URITemplateAction(
                                    label='鬼出櫃',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E9%AC%BC%E5%87%BA%E6%AB%83-the-boogeyman-15081'
                                )
                            ]
                      ),
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/April2023/N2rMWBMdQtlQL3BDdoZi-1080x1539.jpg',
                            title='上映中',
                            text='現正熱映中',
                            actions=[
                                URITemplateAction(
                                    label='色局追兇',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E8%89%B2%E5%B1%80%E8%BF%BD%E5%85%87-360-15061'
                                ),
                                URITemplateAction(
                                    label='厲嬰魂',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E5%8E%B2%E5%AC%B0%E9%AD%82-the-unborn-soul-15145'
                                ),
                                URITemplateAction(
                                    label='駭人古娃娃',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E9%A7%AD%E4%BA%BA%E9%AA%A8%E5%A8%83%E5%A8%83-the-communion-girl-15165'
                                )
                            ]
                      ),
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/April2023/yR8dRQdxuxzPfcZSUyMT-500x714.jpg',
                            title='即將上映',
                            text='近期即將上映',
                            actions=[
                                URITemplateAction(
                                    label='變形金剛:萬獸崛起',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E8%AE%8A%E5%BD%A2%E9%87%91%E5%89%9B-%E8%90%AC%E7%8D%B8%E5%B4%9B%E8%B5%B7-transformers-rise-of-the-beasts-14491'
                                ),
                                URITemplateAction(
                                    label='深夜加油站遇見蘇格拉底',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/%E6%B7%B1%E5%A4%9C%E5%8A%A0%E6%B2%B9%E7%AB%99%E9%81%87%E8%A6%8B%E8%98%87%E6%A0%BC%E6%8B%89%E5%BA%95-peaceful-warrior-15167'
                                ),
                                URITemplateAction(
                                    label='BLUE GIANT藍色巨星',
                                    uri='https://movies.yahoo.com.tw/movieinfo_main/BLUE-GIANT%E8%97%8D%E8%89%B2%E5%B7%A8%E6%98%9F-blue-giant-15234'
                                )
                            ]
                      )     
                    ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
        
def sendActionMovie(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=1') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦動作電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦動作電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))
        
def sendDocumentary(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=16') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦動作電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦動作電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))
        
def sendHorror(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=7') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")


        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦恐怖電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦恐怖電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendFamily(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=11') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦家庭電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦家庭電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendWar(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=13') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦戰爭電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦戰爭電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendAdventure(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=2') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦冒險電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦冒險電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendSciencefiction(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=3') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦科幻電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦科幻電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendFantasy(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=4') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦奇幻電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦奇幻電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendCrime(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=6') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦犯罪電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦犯罪電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendSuspense(event):
    try:
        response = requests.get(
            'https://movies.yahoo.com.tw/moviegenre_result.html?genre_id=8') #動作類型網址
        html = BeautifulSoup(response.text, "html.parser")
        info_contents = html.find_all("div", {"class":"release_info"})
        foto_contents = html.find_all("div", {"class":"release_foto"})
    
        message = TemplateSendMessage(alt_text='以下為推薦懸疑電影',columns=[])
        columns=[]
        foto=[]

            #爬蟲
        for foto_item, info_item in zip(foto_contents, info_contents):
            foto = foto_item.find("img", {"class": "lazy-load"}).get("data-src")

            name = info_item.find("div", {"class": "release_movie_name"}).a.text.strip()
            enName = info_item.find("div", {"class": "en"}).a.text.strip()
            intro = info_item.find("div", {"class": "release_text"}).span.text.strip()
            intro = intro[:40] + '...'
            movie_url = info_item.find("a", {"class": "btn_s_vedio gabtn"}).get("href")

            # 容器

            column = CarouselColumn(
                thumbnail_image_url=foto,
                title=f"{name}",
                text=f"{intro}",
                actions=[
                    URITemplateAction(
                        label='預告片',
                        uri=f"{movie_url}"
                    ),
                    URITemplateAction(
                        label='時刻表',
                        uri='https://www.ezding.com.tw/'
                    )
                ]
            )
            columns.append(column)
        

        carousel_template = CarouselTemplate(columns=columns)  # 創建CarouselTemplate
        message = TemplateSendMessage(alt_text='以下為推薦懸疑電影', template=carousel_template)
                        
    
        line_bot_api.reply_message(event.reply_token, message)
    

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="發生錯誤！"))

def sendPopular(event):
    try:
        message = TemplateSendMessage(
            alt_text='現正熱映電影',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/April2023/GyuSm9varB8vHLw989w1-1080x1600.jpg',
                            title='玩命關頭X',
                            text='迎向終點，就此開始。',
                            actions=[
                                URITemplateAction(
                                    label='點我看預告片',
                                    uri='https://movies.yahoo.com.tw/video/%E7%8E%A9%E5%91%BD%E9%97%9C%E9%A0%ADx-%E6%B3%B0%E7%91%9E%E6%96%AF-%E5%A8%9C%E5%A1%94%E8%8E%89%E8%89%BE%E6%9B%BC%E7%B4%90-%E5%8F%B2%E8%80%83%E7%89%B9%E4%BC%8A%E6%96%AF%E5%A8%81%E7%89%B9%E6%BC%94%E5%93%A1%E5%B0%88%E8%A8%AA-043704968.html?movie_id=14801'
                                ),
                                URITemplateAction(
                                    label='電影時刻表',
                                    uri='https://movies.yahoo.com.tw/movietime_result.html/id=14801'
                                ),
                                URITemplateAction(
                                    label='立即訂票',
                                    uri='https://www.ezding.com.tw/movieInfo?movieid=a612f230dc6d456bb066dd1363d91c78&tab=0'
                                )
                            ]
                      ),
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/March2023/N8fjBYfYsyjE4bYbCcE9-1080x1599.jpg',
                            title='小美人魚',
                            text='現正熱映中',
                            actions=[
                                URITemplateAction(
                                    label='點我看預告片',
                                    uri='https://movies.yahoo.com.tw/video/%E5%B0%8F%E7%BE%8E%E4%BA%BA%E9%AD%9A-%E6%88%90%E7%82%BA%E5%B0%8F%E7%BE%8E%E4%BA%BA%E9%AD%9A%E7%AF%87-034756493.html?movie_id=14619'
                                ),
                                URITemplateAction(
                                    label='電影時刻表',
                                    uri='https://movies.yahoo.com.tw/movietime_result.html/id=14619'
                                ),
                                URITemplateAction(
                                    label='立即訂票',
                                    uri='https://www.ezding.com.tw/movieInfo?movieid=b7557fedadf947dcbc9f4c4a5ad33ce8&tab=0'
                                )
                            ]
                      ),
                    CarouselColumn(
                        thumbnail_image_url='https://movies.yahoo.com.tw/i/o/production/movies/May2023/z1qmfVG9ZY9DpDhEOeXL-1080x1543.JPG',
                            title='犯罪都市3',
                            text='現正熱映中',
                            actions=[
                                URITemplateAction(
                                    label='點我看預告片',
                                    uri='https://movies.yahoo.com.tw/video/%E7%8A%AF%E7%BD%AA%E9%83%BD%E5%B8%823-%E6%BC%94%E5%93%A1%E5%95%8F%E5%80%99%E7%AF%87-002157376.html?movie_id=15208'
                                ),
                                URITemplateAction(
                                    label='電影時刻表',
                                    uri='https://movies.yahoo.com.tw/movietime_result.html/id=15208'
                                ),
                                URITemplateAction(
                                    label='立即訂票',
                                    uri='https://www.ezding.com.tw/movieInfo?movieid=d58404415d354372b6aa2b34a255c453&tab=0'
                                )
                            ]
                      )   
                    ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤!'))
        
