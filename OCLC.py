import urllib2, xml.etree.ElementTree, re



###########
## NOTES ##
###########
"""
xml.dom.minidom is not secure against malicious data

"""

####################
## Response Codes ##
####################

"""
0:  Success. Single-work summary response provided.
2:  Success. Single-work detail response provided.
4:  Success. Multi-work response provided.
    If multi-work is returned, grab owi number from listing, and 
    search by that -- get response code 0, to access DDC
100:    No input. The method requires an input argument.
101:    Invalid input. The standard number argument is invalid.
102:    Not found. No data found for the input argument.
200:    Unexpected error.
"""

################################
## Single-work summary fields ##
################################

"""
author, title, editions, date, format, owi.
ddc is dewey decimal info - "sfa" gives dewey number
lcc is library of congress info 
"""

oclc_base = 'http://classify.oclc.org/classify2/Classify?%s=%s&summary=true'

def getXML(info):
    xdoc = ''
    try:
        url = oclc_base % info
        urlobj = urllib2.urlopen(url)
        data = urlobj.read()
        urlobj.close()
        xdoc = xml.etree.ElementTree.fromstring(data)
    except UnicodeDecodeError:
        print 'UnicodeDecodeError: ' + url
    except IOError:
        print 'IOError: ' + url
    return xdoc

def getTag(xdoc):
    return re.findall('{.*}',xdoc.tag)[0]

def responseCode(xdoc):
    response = xdoc.find('%sresponse' % getTag(xdoc))
    rCode = response.get('code')
    return rCode

def getSingleFromMulti(xdoc):
    rCode = responseCode(xdoc)
    if rCode == '0':
        return xdoc
    elif rCode == '4':
        # get owi value, and search for a work by that
        tag = getTag(xdoc)
        work = xdoc.find('%sworks' % tag) \
                    .find('%swork' % tag)
        owi = work.get('owi')
        newDoc = getXML(('owi',owi))
        if responseCode(newDoc) == '0':
            return newDoc
        else:
            return None
    else:
        return None



def getRecord(xdoc):
    rCode = responseCode(xdoc)
    record = None
    basicInfo = {}
    if rCode == '0':
        tag = getTag(xdoc)
        try:
            work = xdoc.find('%swork' % tag)
            author = work.get('author')
            oneAuthor = author[0:author.find(' |')]
            basicInfo['author'] = oneAuthor
            title = work.get('title')
            basicInfo['title'] = title
            ddcRec = xdoc.find('%srecommendations' % tag) \
                         .find('%sddc' % tag) \
                         .find('%smostPopular' % tag)
            ddc = ddcRec.get('sfa')
            basicInfo['ddc'] = ddc
        except:
            print 'Was only able to extract: %s' % "".join(basicInfo.keys())

    elif rCode == '2':
        print 'Why is there a detailed response here?'
    elif rCode == '4':
        print 'Multi-work response -- cannot obtain single-work'
    elif rCode == '100':
        print 'Missing Input'
    elif rCode == '101':
        print 'Invalid input. The standard number argument is invalid.'
    elif rCode == '102':
        print 'Not Found'
    elif rCode == '200':
        print 'Unexpected error'
    else:
        print 'Unknown response code'

    return basicInfo


