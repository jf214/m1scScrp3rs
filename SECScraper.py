import requests as rq
from bs4 import BeautifulSoup as BS
import pandas as pd
from lxml import html
import json
from selenium import webdriver
from datetime import datetime, timedelta
# ----------------------------------------------------------------------
def GetTickers(companyNames):
    return 0

# ----------------------------------------------------------------------
def GetURLs(tickers,filingType):
    data = []
    secDocumentsXpath = '//*[@id="documentsbutton"]/@href'
    filingsXpath = '//td/a/@href'
    domain = 'http://edgar.sec.gov'

    for tick in tickers:
        secFilingsUrl = 'http://edgar.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='+ tick + '&type=' + filingType
        secFilingsMain = rq.get(secFilingsUrl)
        htmlText = html.fromstring(secFilingsMain.text)
        secDocumentUrls = htmlText.xpath(secDocumentsXpath)
        for docUrl in secDocumentUrls:
            fullDocUrl = domain + docUrl
            secFilingsSub = rq.get(fullDocUrl)
            htmlText = html.fromstring(secFilingsSub.text)
            documentUrls = htmlText.xpath(filingsXpath)
            if '.htm' in documentUrls[0]:
                filingUrl = domain + documentUrls[0]
                values = (tick,filingType, filingUrl)
                data.append(values)
    return data

# ----------------------------------------------------------------------
def GetCompanyFinancials(tickers):
    data = GetURLs(tickers, filingType)
    #productCategoryGrowth = pd.DataFrame()
    i = 0
    for d in data:
        tick = d[0]
        filing = d[1]
        url = d[2]

        # Reads all the tables from the given url and creates a list of dataframes
        df = pd.read_html(url)
        for d in df:
            d = d.replace({'%': None})
            d = d.replace({'$': None})
            d = d.dropna(('index', 'columns'), 'all')
            d = d.reset_index(drop=True)
            test = d.to_string()
            # if tick == 'CDW' and 'NETCOMM PRODUCTS' in test.upper():
            if d.shape[0] > 2 and tick == 'CDW' and 'SMALL BUSINESS' in test.upper():
                d.iloc[[2]] = d.iloc[[2]].shift(1, axis=1)
                d.to_csv('/Users/fuj/Desktop/dataframe_Segments-' + str(i) + '.csv', sep=',', index=False,
                         date_format='%m/%d/%Y')
                i = i + 1
            elif d.shape[0] > 2 and tick == 'NSIT' and 'SALES MIX' in test.upper():
                print (i)
                d.to_csv('/Users/fuj/Desktop/dataframe_Categories-' + str(i) + '.csv', sep=',', index=False,
                         date_format='%m/%d/%Y')
                i = i + 1

# ----------------------------------------------------------------------
def GetCompanyReviews(companyName):

    #
    #
    #
    # Glassdoor won't let me scrape!
    #
    #
    #

    partnerId = '90651'
    key = 'j5OovzNHkFs'
    apiEndpoint =  'http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p='+ partnerId +'&t.k=' + key + '&action=employers&q=' + companyName + '&userip=198.200.139.3&useragent=Mozilla/%2F4.0'

    #Use the API to get the Company Id, create the review URL, then scrape the reviews

    header = {'User-Agent': 'Mozilla/5.0'}
    req = rq.get(apiEndpoint, headers=header)
    jsonString = req.text

    parsedJson = json.loads(jsonString)
    gdCompanyName = parsedJson['response']['employers'][0]['name']
    companyId = parsedJson['response']['employers'][0]['id']
    reviewPage = 1

    reviewUrl = 'https://www.glassdoor.com/Reviews/' + gdCompanyName + '-Reviews-E' + str(companyId) + '_P' + str(reviewPage) + '.htm'
    browser = webdriver.PhantomJS()
    #browser = webdriver.Firefox()
    browser.get(reviewUrl)

    xPathForReviewCount = '//article/div/div/div/h2' #Need to remove ' Employee Reviews'
    xPathForProsAndCons = '//div/div[3]/div/div[2]/div[2]'

    #reviewCount = browser.find_element_by_xpath(xPathForProsAndCons)

    print (browser.page_source)

    #print (reviewCount)


# ----------------------------------------------------------------------
def GetResumesByCompany(companyName):
    #scrape indeed.com?


    #There are 50 resumes per page, loop through 50 at a time

    #get page, scrape xpath, append to list do until scraped list size is 0

    count = 0
    xPathForExperience = '//*[@class="app_name"]'
    scrapedResumes = []
    totalScrapedResumes = 1
    resumeText = []

    while totalScrapedResumes > 0:
        indeedUrlCDW = 'http://www.indeed.com/resumes?q=CDW&co=US&rb=cmpid%3A21779&start=' + str(count)
        indeedResumePage = rq.get(indeedUrlCDW)
        htmlText = html.fromstring(indeedResumePage.text)
        indeedResumeTitleLocation = htmlText.xpath(xPathForExperience)
        totalScrapedResumes = len(indeedResumeTitleLocation)
        scrapedResumes.append(indeedResumeTitleLocation)
        count += 50

    for resumes in scrapedResumes:
        for r in resumes:
            resumeText.append(r.text_content().strip())


    for r in resumeText:
        print (r)

    #postedResumesDf = pd.DataFrame.from_records(resumeText)
    #postedResumesDf.to_csv('/Users/fuj/Desktop/CDWIndeedResumes.csv', sep=',',index=False)  # , date_format='%m/%d/%Y')

    #indeedUrlCDW = 'http://www.indeed.com/resumes?q=CDW&co=US&rb=cmpid%3A21779&start=50'
    ##indeedUrlDiData = 'http://www.indeed.com/resumes?q=Dimension+Data&co=US&rb=cmpid%3A135777'

    return 0
# ----------------------------------------------------------------------
def GetDataCenterLocations():
    #dataCenterMapUrl = 'http://www.datacentermap.com/buildings/usa/'
    #xPathForDcStatesUrl = '//*[@id="dcmcontent"]/div[1]/div/a/@href'
    #xPathForDcCityUrl = '//*[@id="dcmcontent"]/div[1]/div/a/@href'
    #xPathForDcAddress = '//*[@class="DCColumn1"]'

    return 0

# ----------------------------------------------------------------------
def GetCompanyNews(companyName):
    #scrape reuters?
    #reutersNewUrl = 'http://www.reuters.com/finance/stocks/companyNews?symbol=CDW.O&date=08112016'
    return 0

# ----------------------------------------------------------------------
def GetCompanyJobPostings(companyName):

    xPathForCDWJobUrls = '//a/@href' #The list will need to be cleaned up to only include ones with 'Keyword-' in it
    #Also, to get pages add /Page-#/ to the url, until you get an error page
    xPathForCDWJobPostings = '//tr[td]'
    xPathForJobTitle = '//*[@class="coljobtitle"]'
    xPathForJobLocation = '//*[@class="collocation"]'
    xPathForJobCategory = '//*[@class="colshorttextfield1"]'

    cdwJobPostingSite = 'http://www.cdwjobs.com/List/Custom/Job-Category'
    YMD = '20010101'
    dateObject = datetime.strptime(YMD,'%Y%m%d')
    today = datetime.now()
    historicalUrls = []
    dates = []
    i = 0
    postedJobTitles = []
    postedJobLocations = []

    while dateObject < today:
        wayBackMachineApiUrl = 'http://archive.org/wayback/available?url=' + cdwJobPostingSite + '&timestamp=' + YMD
        resp = rq.get(wayBackMachineApiUrl)
        formattedJson = json.loads(resp.text)
        timeStamp = formattedJson['archived_snapshots']['closest']['timestamp']
        print (timeStamp)
        historicalUrl = formattedJson['archived_snapshots']['closest']['url']
        dateObject = datetime.strptime(YMD,'%Y%m%d')
        dateObject += timedelta(days=5)
        YMD = dateObject.strftime('%Y%m%d')
        if historicalUrl not in historicalUrls:
            YMD = timeStamp[:8]
            historicalUrls.append(historicalUrl)

    for url in historicalUrls:
        resp = rq.get(url)
        htmlText = html.fromstring(resp.text)
        cdwJobsUrls = htmlText.xpath(xPathForCDWJobUrls)

        for jobUrl in cdwJobsUrls:
            if 'Keyword-' in jobUrl:
                fullJobUrl = 'http://web.archive.org' + jobUrl
                jobDate = jobUrl[5:13]
                print (jobUrl)
                jobDateObject = datetime.strptime(jobDate , '%Y%m%d')
                print(jobDate)
                resp1 = rq.get(fullJobUrl)
                htmlText = html.fromstring(resp1.content)
                postedJobTitlesRaw = htmlText.xpath(xPathForJobTitle)
                postedJobLocationsRaw = htmlText.xpath(xPathForJobLocation)
                #postedJobCategoriesRaw = htmlText.xpath(xPathForJobCategory)

                for rawJobTitle in postedJobTitlesRaw:
                    postedJobTitles.append(rawJobTitle.text_content().strip())

                for rawJobLocation in postedJobLocationsRaw:
                    postedJobLocations.append(rawJobLocation.text_content().strip())
                    dates.append(jobDateObject)

                postedJobs = zip(postedJobTitles, postedJobLocations, dates)
                postedJobsDf = pd.DataFrame.from_records(postedJobs)

                postedJobsDf.to_csv('/Users/fuj/Desktop/CDWHistoricalJobPostings.csv', sep=',', index=False) #, date_format='%m/%d/%Y')


    return 0

# ----------------------------------------------------------------------
if __name__ == "__main__":
    filingType = '10-K'


    #companyNames = ['Shi-International-Corporation', 'Cdw']

    #GetCompanyReviews('CDW')

    #GetCompanyFinancials('CDW')

    #GetCompanyJobPostings('CDW')

    #GetResumesByCompany('CDW')