# -*- coding: utf-8 -*-
import scrapy
import codecs
import requests
from bs4 import BeautifulSoup
import pymysql


# 城市对象模型
class City:
    def __init__(self, name, url):
        self.name = name
        self.url =url


class MonitoringSiteInfo:
    def __init__(self, releaseTime, cityName, siteName, AQI, desc, mainPollution, pm25, pm10, co, no2, o3, o3_8, so2):
        self.releaseTime = releaseTime
        self.cityName = cityName
        self.siteName = siteName
        self.AQI = AQI
        self.desc = desc
        self.mainPollution = mainPollution
        self.pm25 = pm25
        self.pm10 = pm10
        self.co = co
        self.no2 = no2
        self.o3 = o3
        self.o3_8 = o3_8
        self.so2 = so2


# 爬虫程序
class GetcitySpider(scrapy.Spider):

    print("ivanl000001")

    # 爬虫相关
    name = 'getCity'
    allowed_domains = ['http://pm25.in']
    start_urls = ['http://pm25.in']


    # 解析结果
    def parse(self, response):

        print("----------------------------spider-start----------------------------")

        # 0, 连接数据库
        database = pymysql.connect("127.0.0.1", "root", "ivanl48265", "test", charset='utf8')
        cursor = database.cursor()

        #1，xpath获取所有的城市名
        cityNameList = response.xpath('/html/body/div[2]/div[2]/div[2]/div[2]/ul[@class="unstyled"]/div[2]/li/a/text()').extract()

        #2，xpath获取所有的城市对应数据的url
        # 在a前面用//居然ok了， 嗷嗷嗷！！！
        urlList = response.xpath('/html/body/div[2]/div[2]/div[2]/div[2]/ul[@class="unstyled"]/div[2]/li//a/@href').extract()

        #3，保存城市和url数据
        cities = []
        for i in range(len(cityNameList)):
            city = City(cityNameList[i], "http://pm25.in"+urlList[i])
            cities.append(city)
            # break # 这里break是为了测似乎的时候只走第一次

        #4, 写入保存的数据到文件中(其实这里存不存都无所谓)
        # for city in cities:
        #
        #     #保存到数据库中去, 其实保存一遍也就够了， 当有一天不能访问的时候重新更新一下， 不过这种情况应该会很少会遇到
        #     print(city.name)
        #     print(city.url)
        #     sqlStr = "insert into cityInfo (cityName, url) VALUES ('%s', '%s')" % (city.name, city.url)
        #     cursor.execute(sqlStr)
        #     database.commit()
        #     print("保存数据库--")
            # return

        #     print("城市名："+city.name+",url："+city.url)
        #     lineTxt = city.name+" "+city.url+"\n"
        #     f = codecs.open("cityInfo.txt", "a", "utf-8")
        #     f.write(lineTxt)
        #     f.close()

        # #5，开始遍历获取每个城市的空气质量数据
        monitoringSiteInfos = []  # 因为监测站不是某一个城市所有，所以放在最外面
        for city in cities:
            print(city.url)


            returnedData = requests.get(city.url)
            print(returnedData.status_code)
            if returnedData.status_code != 200:
                print(city.name + "," + city.name + ":" + "请求出错！")
                break
            content = returnedData.content.decode("utf8")
            soup = BeautifulSoup(content, "html.parser")

            # print("soup:\n"+soup.text)
            # thead那些标题都是死的，所以这里就不再抓取，直接定义就好了
            # tableHead = soup.thead
            # print("tableHead:\n"+tableHead)

            #5.1, 首先获取发布时间
            dataReleaseTimeSoup = soup.find(attrs={"class": "live_data_time"})
            releaseTimeStr = dataReleaseTimeSoup.contents[1].text
            print("releaseTimeStr:\n"+releaseTimeStr)

            #5.2, 然后获取监测站及相关信息
            print("--------------------------------------monitoringSite---------start----------------------------------------")
            monitoringSitesSoup = soup.find("tbody").children

            i = 0  # 这个用来排除空行的影响
            j = 0  # 这个用来判断某个城市监测站的数量
            # 下面是遍历该城市中的每个监测站， 并取出数据
            for monitoringSiteSoup in monitoringSitesSoup:
                i += 1
                # 这里判断的目的是去除空行的那些
                if i%2 == 0:
                    # print("000000000")
                    j = j+1
                    print(monitoringSiteSoup.find_all('td'))
                    monitoringSiteInfo = monitoringSiteSoup.find_all('td')
                    name = monitoringSiteInfo[0].text.replace(' ','')
                    AQI = monitoringSiteInfo[1].text.replace(' ','')
                    desc = monitoringSiteInfo[2].text.replace(' ','')
                    mainPollution = monitoringSiteInfo[3].text.replace(' ','')
                    pm25 = monitoringSiteInfo[4].text.replace(' ','')
                    pm10 = monitoringSiteInfo[5].text.replace(' ','')
                    co = monitoringSiteInfo[6].text.replace(' ','')
                    no2 = monitoringSiteInfo[7].text.replace(' ','')
                    o3 = monitoringSiteInfo[8].text.replace(' ','')
                    o3_8 = monitoringSiteInfo[9].text.replace(' ','')
                    so2 = monitoringSiteInfo[10].text.replace(' ','')
                    #print(name)
                    print(releaseTimeStr + "--" + name + "--" + AQI + "--" + desc + "--" + mainPollution + "--" + pm25 + "--" + pm10 + "--" + co + "--" + no2 + "--" + o3 + "--" + o3_8 + "--" + so2 )
                    monitoringSiteInfoModel = MonitoringSiteInfo(releaseTimeStr, city.name, name, AQI, desc, mainPollution, pm25, pm10, co, no2, o3, o3_8, so2)
                    monitoringSiteInfos.append(monitoringSiteInfoModel)

                print(i)

                print("监测站开始------------------------------")
                print(city.name + "，监测站数量：" + str(j))
                print("监测站结束------------------------------")

            print("--------------------------------------monitoringSite----------end---------------------------------------")

            # return

        #6， 把获取的全国城市空气质量保存到文件中
        for monitoringSiteInfo in monitoringSiteInfos:
            # 6.1， 写入到文件中
            # lineTxt = monitoringSiteInfo.releaseTime + " " + monitoringSiteInfo.cityName + " " + monitoringSiteInfo.siteName + " "  +monitoringSiteInfo.AQI + " " +monitoringSiteInfo.mainPollution+ " "+ monitoringSiteInfo.desc + " " + monitoringSiteInfo.pm25 + " " + monitoringSiteInfo.pm10 + " " + monitoringSiteInfo.co + " " + monitoringSiteInfo.no2 + " " + monitoringSiteInfo.o3 + " " + monitoringSiteInfo.o3_8 + " " + monitoringSiteInfo.so2 + "\n"
            # f = codecs.open("api.txt", "a", "utf-8")
            # f.write(lineTxt)
            # f.close()

            # 6.2, 写入到数据库中
            sqlStr = "insert into cityAPIInfo (releaseTime, cityName, monitoringSiteName, AQI, pollutionLevel, mainPollution, pm25, pm10, carbonMonoxide, no2, o3, o3_8, so2) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (monitoringSiteInfo.releaseTime, monitoringSiteInfo.cityName, monitoringSiteInfo.siteName, monitoringSiteInfo.AQI, monitoringSiteInfo.desc, monitoringSiteInfo.mainPollution, monitoringSiteInfo.pm25, monitoringSiteInfo.pm10, monitoringSiteInfo.co, monitoringSiteInfo.no2, monitoringSiteInfo.o3, monitoringSiteInfo.o3_8, monitoringSiteInfo.so2)
            row = cursor.execute(sqlStr)
            database.commit()
            print("保存数据库--" + str(row))

        print("全国监测站一共有：" + str(len(monitoringSiteInfos)))
        database.close()
        print("----------------------------spider-end----------------------------")
        pass
