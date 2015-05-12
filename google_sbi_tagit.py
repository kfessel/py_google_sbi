#!/usr/bin/python
'''module and stand alone application to access google sbi'''
import sys

config={"stopwordfilter":True,"Nimgres":80,"NThreads":5,"NTop":10}

#Google does some filtering on the userangent (it does not like to be asked by CURL or just Mozilla/5.0)
#useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36'
useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40'
cookiejar = "kekstopf"

def curl_get(url):
    ''' gets an url using curl returns a string containing the result'''
    import pycurl
    try:
        #python3
        from io import BytesIO
    except ImportError:
        #python2
        from StringIO import StringIO as BytesIO

    try:
        # python 3
        from urllib.parse import urlencode
    except ImportError:
        # python 2
        from urllib import urlencode
    
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL,url)
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    #Google is unsing a redirect page as reply 
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.COOKIEJAR, cookiejar)
    #Google does some filtering on the useragent (it does not like to be asked by CURL or just Mozilla/5.0)
    curl.setopt(curl.USERAGENT, useragent)
    curl.perform()
    curl.close()

    return buffer.getvalue().decode('utf8')

def loadconfig(configstr):
    '''loads module configuration from a json string
    e.g.: '{"stopwordfilter":false,"Nimgres":60,"NThreads":5,NTop:10}'''
    import json
    global config
    cfg= json.loads(configstr)
    
    if 'stopwordfilter' in cfg:
        config['stopwordfilter']=bool(cfg['stopwordfilter'])
    
    for name in [ 'Nimgres', 'NThreads', 'NTop' ]:
        if name in cfg:
            config[name]= int(cfg[name])
    
    print (config)
    '''
    config = {  "stopwordfilter":bool(cfg['stopwordfilter']),
                "Nimgres":int(cfg['Nimgres']),
                "NThreads":int(cfg['NThreads']),
                "NTop":int(cfg['NTop'])
              }
    '''
    

def sanatizegoogleurl(url):
    '''replaces &amp; in url retrived from google''' 
    import re
    return re.sub(r"&amp;","&", url)

def imgresurlprocessor(url):
    '''
        processes an imageres url
        gets the contend useing curl_get
        searches the description of that picture
        splits that desciption into word and bigrams
        if stopword filter is enabled it removes the stopword from words and stopword containing bigrams from bigrams
    '''
    import re
    page = curl_get(url)
    descriptions = re.findall("<p class=il_n>([^<]*)</p>",page)
    description = ''
    for i in descriptions:
      description += " " + i.lower()
    descriptionwords = re.findall(r'\w+',description,re.UNICODE)
    descriptionbigrams = []
    for i in range(len(descriptionwords)-1):
      descriptionbigrams.append(descriptionwords[i] +  " " + descriptionwords[i + 1])
    
    if config['stopwordfilter']:
        from nltk.corpus import stopwords
        stop_words = stopwords.words()
        pattern = r'|'.join(stop_words)
        pattern = r'\b(' +pattern + r')\b'
        prog = re.compile(pattern, re.IGNORECASE)
        words=[i for i in descriptionwords if not prog.search(i)]
        bigrams=[i for i in descriptionbigrams if not prog.search(i)]
        #words = filter(lambda x: not prog.search(x), descriptionwords)
        #bigrams = filter(lambda x: not prog.search(x), descriptionbigrams)
    else:
        words = descriptionwords
        bigrams = descriptionbigrams
    
    return description, words, bigrams




def nameit(picture_buffer, hint=None):
    '''uploads a picture to google search by image 
        gives google a hint for intrpretation if given
        gets googles search tags if it assigned some 
        gets preprocessed image descriptions by invoking imgresurlprocessor
        returns googles tags and most common words and bigrams
    '''
    import re
    import pycurl
    try:
        #python3
        from io import BytesIO
    except ImportError:
        #python2
        from StringIO import StringIO as BytesIO
        
    try:
        # python 3
        from urllib.parse import urlencode
    except ImportError:
        # python 2
        from urllib import urlencode
    
    buffer = BytesIO()
    curl = pycurl.Curl()
    
    headers = {}
    def decodeHeader(header_line):
        
        # HTTP standard specifies that headers are encoded in iso-8859-1.
        # On Python 2, decoding step can be skipped.
        # On Python 3, decoding step is required.
        header_line = header_line.decode('iso-8859-1')

        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines...
        if ':' not in header_line:
            return

        # Break the header line into header name and value.
        name, value = header_line.split(':', 1)

        # Remove whitespace that may be present.
        # Header lines include the trailing newline, and there may be whitespace
        # around the colon.
        name = name.strip()
        value = value.strip()

        # Header names are case insensitive.
        # Lowercase name here.
        name = name.lower()

        # Now we can actually record the header name and value.
        headers[name] = value  
    
    #postdict=[("encoded_image", (curl.FORM_FILE,picture_file)),]
    postdict=[("encoded_image", (pycurl.FORM_BUFFER, "picture", pycurl.FORM_BUFFERPTR, picture_buffer)),]
    
    curl.setopt(curl.URL,"https://www.google.com/searchbyimage/upload")
    curl.setopt(curl.WRITEFUNCTION, buffer.write)
    #Google is unsing a redirect page as reply
    curl.setopt(curl.FOLLOWLOCATION, True)
    curl.setopt(curl.COOKIEJAR, cookiejar)
    #Google does some filtering on the useragent (it does not like to be asked by CURL or just Mozilla/5.0)
    curl.setopt(curl.USERAGENT, useragent)
    curl.setopt(curl.HTTPPOST, postdict)
    curl.setopt(curl.HEADERFUNCTION, decodeHeader)
    curl.perform()
    curl.close()
    
    page = buffer.getvalue().decode('utf8')
    #print hint
    #print headers
    
    if hint!= None:
        durl = headers['location']+'&'+urlencode([('q',hint)])
        print (durl)
        page=curl_get(durl)
    
    #export googles response (not the redirect page)
    f = open("page.htm","w")
    f.write(page.encode('utf8'))
    f.close()
    
    
    #Regex for /search?q=neue+5+euro+schein& (which is the blue text link to search the image content @google)
    #<a class="_gUb" href="/search?q=neue+5+euro+schein&amp;sa=X&amp;ei=7GIdVfugMcGfsAHql4PYAg&amp;ved=0CB0QvQ4oAA" style="font-style:italic">neue 5 euro schein</a>
    
    out=re.findall(r"<a class=\"_gUb\" [^>]*>([^<]*)</a>", page)
    out1=re.findall(r"<h3 class=\"r\"><a href=\"([^\"]*)\"",page)
    out2=[sanatizegoogleurl(url) for url in re.findall(r'http[^\"]*imgres[^\"]*',page)]
    out3=re.findall(r'title="(htt[^"]*)', page)
    
    #what would google tag this?
    if len(out)<1:
      out=[]
    else:
      out=out[0]
      out=re.split('\W+',out,re.UNICODE)
    
    imgreses=config["Nimgres"]
    
    if len(out2)<imgreses:
      #find the  similar pictures link and follow
      similarpicturesurl=re.search(r"\/search\?tbs=simg:[^\">]*",page)
      if similarpicturesurl:
            similarpicturesurl=similarpicturesurl.group(0)
            similarpicturesurl="https://www.google.com"+sanatizegoogleurl(similarpicturesurl)
            oldlen=len(out2)
            
            simpage=curl_get(similarpicturesurl)
            out2=[sanatizegoogleurl(url) for url in re.findall(r'http[^\"]*imgres[^\"]*',simpage)]
            
            for i in range(1, 20):
                if not len(out2)>oldlen or len(out2) >= imgreses:
                    break 
                oldlen=len(out2)
                simpage=curl_get(similarpicturesurl + "&ijn=" + str(i) + "&start=" + str(i*100))
                out2.extend(map(sanatizegoogleurl,re.findall(r'http[^\"]*imgres[^\"]*',simpage)))
    #get imgreses image results and read the desciptions count words and bigrams
    
    #out4=[]
    #for i in out2:
      #if len(out4)>=imgreses:
        #break
      #i=re.sub(r"&amp;","&", i)
      ##print i
      #print ".",
      #sys.stdout.flush()
      #imgrespage=curl_get(i)
      #imgdescription=re.findall("<p class=il_n>([^<]*)</p>",imgrespage)
      #out4.append("".join(imgdescription))
    #alldescriptions =  ""
    #for i in out4:
      #alldescriptions += " " + i.lower() 
    
    #descriptionwords=re.findall(r'\w+',alldescriptions,re.UNICODE)
    #descriptionbigrams=[]
    #for i in range(len(descriptionwords)-1):
      #descriptionbigrams.append(descriptionwords[i]+ " " + descriptionwords[i+1])

    
    #parallel version
    out4=[]
    imgresurls=out2[0:imgreses]
    NThreads=config['NThreads']
    from multiprocessing import Pool
    print ("processing",len(imgresurls), "URLs using",  NThreads, "Threads",)
    sys.stdout.flush()
    p = Pool(NThreads)
    imgresurlsprocessed = p.map(imgresurlprocessor, imgresurls)
    #imgresurlsprocessed = list(map(imgresurlprocessor, imgresurls))
    p.close()
    print ("done")
    descriptions=[]
    descriptionwords=[]
    descriptionbigrams=[]
    for i in imgresurlsprocessed:
      imgdescription, imgwords, imgbigrams = i
      descriptions.extend(imgdescription)
      descriptionwords.extend(imgwords)
      descriptionbigrams.extend(imgbigrams)
    
    #http://stackoverflow.com/questions/15524030/counting-words-in-python
    from collections import Counter
    out4=descriptions
    out5=Counter(descriptionwords).most_common(config['NTop'])
    out6=Counter(descriptionbigrams).most_common(config['NTop'])
    
    return out,out5,out6



def main(argv):
    ''' main for standalone usage
        interprete parameters
        snaps a picture if requested to a given filename
        loads a picture from a file
        calls nameit for the picture using a hint if given
        prints the result
    '''
    import os
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Take Pictures and ask Google to name them')
    parser.add_argument('-s', '--snap', action='store_true', help='take a snapshot')
    parser.add_argument('-c', '--cam', nargs='?', type=int, help='use cam Number N defaults to 0', default=0)
    parser.add_argument('-b', '--config', nargs='?', type=str, help='JSON configuration string \'{"stopwordfilter":false,"Nimgres":60,"NThreads":5,"NTop":10}\'')
    parser.add_argument('-a', '--hint', nargs='?', type=str, help='give an interpretation hin', default=None)
    parser.add_argument('NAME', nargs='?', help='Filename defaults to snap.jpg', default="snap.jpg")
    
    cmdline_args = parser.parse_args(sys.argv[1:]) #cut the program-name off the list 
    
    if cmdline_args.config:
        loadconfig(cmdline_args.config)
    
    print (config)
    
    picture_file=cmdline_args.NAME
    hint = cmdline_args.hint
    
    if cmdline_args.snap:
      from snapshot import snapshot
      snapshot(picture_file,cmdline_args.cam)
    
    if not os.path.exists(picture_file):
      print ("missing " + picture_file + " you may want to capture it using -s (-h for Help)")
      sys.exit(-1)
    
    image_file = open(picture_file,'rb')
    image_buffer=image_file.read()
    ret = nameit(image_buffer,hint)
    image_file.close()
    for j in ret:
      for i in j:
        print (i)
      print ("" , len(j),  "################################################################")

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))