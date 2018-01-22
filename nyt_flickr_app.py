import requests
import json

NYT_CACHE_FNAME   = "article_raw_data.json"       #Cache file from New York Times
FLRK_CACHE_FNAME  = "flickr_raw_data.json"        #Cache file from Flickr: Search result of 5 most keywords
PHOTO_CACHE_FNAME = "photo_data.json"             #Cache file from Filckr: Search result of 20 photos' information of each keyword

#1st Class: Article
class Article:
    #Constructor
    def __init__(self, headline, url, abstract, keywords):
        self.headline = headline
        self.url = url
        self.abstract = abstract
        self.keywords = keywords    #List of article keywords
        self.num_of_keywords = len(keywords)

    #String method
    def __str__(self):
        keyword_str = ', '.join(self.keywords)
        information = "headline: "+self.headline+"\n"+"url: "+self.url+"\n"+"abstract: " + self.abstract + "\n"+\
                      "keywords: "+keyword_str+" ("+str(self.num_of_keywords)+")"+"\n"
        return information

    # Find the longest word in the abstract
    def find_longest_word(self):
        current_longest = max(self.abstract.split(), key=len)
        return current_longest


#2nd Class: Photo
class Photo:
    #Constructor
    def __init__(self, id, owner, title, secret,):
        self.id = id
        self.username = ""
        self.title = title
        self.secret = secret
        self.taken_date = ""
        self.tags = []
        self.num_of_tags = 0
        self.tags_str = ""

    # String method
    def __str__(self):
        information = "title: " + self.title + "\n" + "username: " + self.username + "\n" + "date: " + self.taken_date + "\n" + \
                       "tags: " + self.tags_str + " (number of tags: " + str(self.num_of_tags) + ")" + "\n"
        return information

    #Make REST API request to get more information about photo (username, date, tags)
    def request_more_photo_info(self):
        try:
            f = open(PHOTO_CACHE_FNAME, 'r')        #Open a file 'PHOTO_CACHE_FNAME'
            content = f.read()                      #Read the file
            PHOTO_CACHE_DIC = json.loads(content)   # Load the string into a Python object, saved in a variable called CACHE_DICTION.
        except:
            PHOTO_CACHE_DIC = {}

        # Get more data about the photo
        base_url = "https://api.flickr.com/services/rest/"
        params_d = {}
        params_d["api_key"] = flickr_key
        params_d['format'] = "json"
        params_d["method"] = "flickr.photos.getInfo"
        params_d["photo_id"] = str(self.id)
        params_d["secret"] = str(self.secret)

        #make unique indent. to use in cache file.
        unique_ident = params_unique_combination(base_url, params_d)
        if unique_ident in PHOTO_CACHE_DIC:
            python_flickr = PHOTO_CACHE_DIC[unique_ident]
        else:
            resp = requests.get(base_url, params=params_d)
            resp_str = resp.text
            python_flickr = json.loads(resp_str[14:-1])
            PHOTO_CACHE_DIC[unique_ident] = python_flickr

            f = open(PHOTO_CACHE_FNAME, "w")       #Cache File
            cache_str_tmp = json.dumps(PHOTO_CACHE_DIC)
            f.write(cache_str_tmp)
            f.close()

        # Get photo's more info (tags, num of tags etc.)
        self.username = PHOTO_CACHE_DIC[unique_ident]["photo"]["owner"]["username"]
        self.taken_date = PHOTO_CACHE_DIC[unique_ident]["photo"]["dates"]["taken"]

        for tag in range(len(PHOTO_CACHE_DIC[unique_ident]["photo"]["tags"]["tag"])):
            self.tags.append(PHOTO_CACHE_DIC[unique_ident]["photo"]["tags"]["tag"][tag]["raw"])

        self.num_of_tags = self.count_tags()
        self.tags_str = '/ '.join(self.tags)
        # print(self.tags_str)

    def count_tags(self):
        return len(self.tags)


#########################################################################################
#########################################################################################
#unique representation which is used in cache file
def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabet_keys = sorted(params_d.keys())
    res = []
    for k in alphabet_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return(baseurl + "_".join(res))

#NYT ArticleSearch API
def get_article_data(param_code):
    my_api_key = '&api-key=4e0cd86f2a104bf593e49a2eea58931d'
    my_base_url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?'

    article_response = requests.get(my_base_url+my_api_key+'&q='+param_code)
    article_data = json.loads(article_response.text)

    f = open(NYT_CACHE_FNAME, "w")
    cache_str_tmp = json.dumps(article_data)
    f.write(cache_str_tmp)
    f.close()

#Get meaningful data from result of get_article_data()
def filter_article_data(file_name):
    try:
        f = open(file_name, 'r')            #Open a file [file_name].
        content = f.read()                  #Read the file.
        CACHE_DIC = json.loads(content)     #Load the string into a Python object.
    except:
        CACHE_DIC = {}

    #Get article's info
    tups_list = []
    for item in range(len(CACHE_DIC["response"]["docs"])):
        headline = CACHE_DIC["response"]["docs"][item]["headline"]["main"]
        url = CACHE_DIC["response"]["docs"][item]["web_url"]
        abstract = CACHE_DIC["response"]["docs"][item]["snippet"]
        keywords = []
        for word in range(len(CACHE_DIC["response"]["docs"][item]["keywords"])):
            keywords.append(CACHE_DIC["response"]["docs"][item]["keywords"][word]["value"])
        tups_list.append((headline, url, abstract, keywords))

    return tups_list

#########################################################################################
#########################################################################################
#Flickr API
flickr_key = "18a44a884af45f11c469e243e80ce7c7"
flickr_secret = "b503d1ee475edd58"

def get_flickr_data(wrd, opt=20):
    try:
        f = open(FLRK_CACHE_FNAME, 'r')  #Open a file
        content = f.read()  #Read the file
        FLRK_CACHE_DIC = json.loads(content)
    except:
        FLRK_CACHE_DIC = {}

    base_url = "https://api.flickr.com/services/rest/"
    params_d = {}
    params_d["api_key"] = flickr_key
    params_d['format'] = "json"
    params_d["tags"] = wrd
    params_d["tag_mode"] = "all"
    params_d["method"] = "flickr.photos.search"
    params_d["per_page"] = opt

    unique_ident = params_unique_combination(base_url, params_d)
    if unique_ident in FLRK_CACHE_DIC:
        python_flickr = FLRK_CACHE_DIC[unique_ident]
    else:
        resp = requests.get(base_url, params = params_d)
        resp_str = resp.text
        python_flickr = json.loads(resp_str[14:-1])
        FLRK_CACHE_DIC[unique_ident] = python_flickr
        # print(python_flickr)

        f = open(FLRK_CACHE_FNAME, "w")
        cache_str_tmp = json.dumps(FLRK_CACHE_DIC)
        f.write(cache_str_tmp)
        f.close()

#Get meaningfult data from the result of get_flickr_data()
def filter_flickr_data(file_name, keyword):
    try:
        f = open(file_name, 'r')
        content = f.read()
        CACHE_DIC = json.loads(content)
    except:
        CACHE_DIC = {}

    #unique
    base_url = "https://api.flickr.com/services/rest/"
    params_d = {}
    params_d["api_key"] = flickr_key
    params_d['format'] = "json"
    params_d["tags"] = keyword
    params_d["tag_mode"] = "all"
    params_d["method"] = "flickr.photos.search"
    params_d["per_page"] = 20
    unique_ident = params_unique_combination(base_url, params_d)

    #Get photo's info
    tups_list = []

    for item in range(len(CACHE_DIC[unique_ident]["photos"]["photo"])):
        id = CACHE_DIC[unique_ident]["photos"]["photo"][item]["id"]
        owner = CACHE_DIC[unique_ident]["photos"]["photo"][item]["owner"]
        title = CACHE_DIC[unique_ident]["photos"]["photo"][item]["title"]
        secret = CACHE_DIC[unique_ident]["photos"]["photo"][item]["secret"]

        tups_list.append((id, owner, title, secret))

    return tups_list

#########################################################################################
#########################################################################################
#Main Function

#Get data from API
get_article_data('google')  #Get Data from API
article_info_tups_list = filter_article_data(NYT_CACHE_FNAME) #Get filtered data
article_insts_list = [] #List of Article instances

#Construct Article instances
for tup in article_info_tups_list:
    article_insts_list.append(Article(tup[0], tup[1], tup[2], tup[3]))

######Sorting articles: Sorting by number of keywords and break ties alphabetically by article title
article_insts_list= sorted(article_insts_list, key=lambda article: (-article.num_of_keywords, article.headline))

######Invoke the string method of Article
print("********************************")
print("****Result of Article Search****")
print("********************************")
for article in article_insts_list:
    print(article)

#Get the longest word of each abstract of the 5 articles with the most keywords.
longest_keywords_list = []
print("******5 Longest Keywords******")
for i in range(0, 5):
    longest_keywords_list.append(article_insts_list[i].find_longest_word())
    print(longest_keywords_list[i])

#For each of those words, make a search on Flickr.
photo_info_tups_list=[]
photo_insts_list = [] #List of Article instances

for i in range(0, 5):
    get_flickr_data(longest_keywords_list[i])   #Request data from REST API and save at cache file
    photo_info_tups_list.append(filter_flickr_data(FLRK_CACHE_FNAME, longest_keywords_list[i]))  # Get filtered data from the cache file.

#Make the photo instances by these information.
for tup_list in photo_info_tups_list:
    for tup in tup_list:
        photo_insts_list.append(Photo(tup[0], tup[1], tup[2], tup[3]))

#Get more data by requesting data from REST API and save at a cache file.
for photo in photo_insts_list:
    photo.request_more_photo_info()
    # print("["+str(i)+"]" + str(photo.num_of_tags))

#Sorting by number of tags
photo_insts_list= sorted(photo_insts_list, key=lambda photo: photo.num_of_tags)

######Invoke the string method of Photo
print("********************************")
print("*****Result of Photo Search*****")
print("********************************")
for photo in photo_insts_list:
    print(photo)

# Write a .CSV file about those photos, with clear headers:
csvfile = open('photo_information.csv', 'w', -1, "utf-8")
csvfile.write('Photo title, Username, Tags, Number of Tags, Date\n')
for photo in photo_insts_list:
    csvfile.write('{}, {}, {}, {}, {}\n'.format("\""+photo.title+"\"", photo.username, photo.tags_str, photo.num_of_tags, photo.taken_date))
csvfile.close()





