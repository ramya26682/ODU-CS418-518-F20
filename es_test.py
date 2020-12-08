from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch
from django.core.paginator import Paginator, Page
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.paginator import Paginator, Page
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch

elasticIndex = "search"

class esPaginator:
    def __init__(self, totalResults = 0, perPage=10):
        self.count = totalResults
        self.perPage = perPage
        self.num_pages = totalResults//perPage
        
        self.paginator = {
            'number' : 0,
            'count' : totalResults,
            'has_other_pages':False,
            'has_previous':False,
            'get_prev_page':0,
            'has_next':False,
            'get_next_page':0,
            'get_page_range':0,
            'num_pages' : 1,
        }
    def paginate(self, number):
        if self.count > self.perPage:
            self.paginator['has_other_pages'] = True
            self.paginator['has_previous'] = True if number > 1 else False
            self.paginator['has_next'] = True if number < (self.num_pages + 1) else False
            self.paginator['num_pages'] = self.count//self.perPage + 1
            self.paginator['get_page_range'] = list(range(1,self.paginator['num_pages']+1))
            if number in self.paginator['get_page_range']:
                self.paginator['number'] = number
                self.paginator['get_prev_page'] = number - 1
                self.paginator['get_next_page'] = number + 1
            else:
                self.paginator['number'] = 1
                self.paginator['get_prev_page'] = 1
                self.paginator['get_next_page'] = 1
            return self.paginator
        return self.paginator

def AdvancedSearch(patentID="", aspect="",pageLowerLimit=0, pageUpperLimit=10, page=1):
    client = Elasticsearch()
    query_data = Q("bool", should=[Q("match", patentID=patentID),Q("match", aspect=aspect)],minimum_should_match=1)
    look = Search(using=client, index="search").query(query_data)[pageLowerLimit:pageUpperLimit]
    response = look.execute()
    totalResults=response.hits.total.value
    print(totalResults)
    paginator = esPaginator(totalResults = totalResults, perPage = 10)
    posts = paginator.paginate(page)
    search=get_results(response)
    return totalResults, search, posts

def get_results(response):
    results=[]
    for field in response:
        result_tuple = (field.patentID + ' ' + field.pid, field.is_multiple, field.patentID+ '-D0' +field.pid[2:]+'.png',field.aspect)
        results.append(result_tuple)
    return results



def Singlesearch(Q_text="",pageLowerLimit = 0, pageUpperLimit = 10, page=1):
    client = Elasticsearch()
    query = MultiMatch(query=Q_text, fields=['patentID', 'pid','origreftext','description','aspect'], fuzziness='AUTO')
    look = Search(using=client, index='search').query(query)[pageLowerLimit:pageUpperLimit]
    response = look.execute()
    totalResults = response.hits.total.value
    print(totalResults)
    paginator = esPaginator(totalResults = totalResults, perPage = 10)
    posts = paginator.paginate(page)
    search=get_results(response)
    return totalResults, search, posts

def updateIndex(data):
    client = Elasticsearch()
    newPatent = {
        "patentID": data['patentID'],
        "pid": data['pid'],
        "is_multiple": data['is_multiple'],
        "origreftext": data['origreftext'],
        "figid": data['figid'], 
        "subfig": data['subfig'], 
        "is_caption": data['is_caption'], 
        "description": data['description'], 
        "aspect": data['aspect'], 
        "object": data['objects']
    }
    response = client.index(
        index = 'search',
        doc_type = '_doc',
        body = newPatent
    )
    print(response)
    if response['result'] == "created":
        print('--> created')
        return True
    else:
        return False



# elastic-search paginator class



# Index new Data



# def eSearchNormalRetrieve(searchTerm="", pageLowerLimit = 0, pageUpperLimit = 10, page=1):
#     client = Elasticsearch()
#     q = MultiMatch(query=searchTerm, 
#                    fields=['patentID', 
#                            'pid',
#                            'origreftext',
#                            'description',
#                            'aspect', 
#                            'object'],
#                    fuzziness='AUTO')
#     s = Search(using=client, index=elasticIndex).query(q)[pageLowerLimit:pageUpperLimit]
#     response = s.execute()
#     print('Total hits found : ', response.hits.total)
#     totalResults = response.hits.total.value
#     paginator = esPaginator(totalResults = totalResults, perPage = 10)
#     posts = paginator.paginate(page)
#     search=get_results(response)
#     return totalResults, search, posts

# def eSearchAdvancedRetrieve(imgPatentId="", imgDescription="", imgObject="", imgAspect="", pageLowerLimit = 0, pageUpperLimit = 10, page=1):
#     client = Elasticsearch()
#     q = Q("bool", 
#           should=[
#               Q("match", patentID=imgPatentId),
#               Q("match", description=imgDescription),
#               Q("match", object=imgObject),
#               Q("match", aspect=imgAspect),
#             ],
#           minimum_should_match=1)
#     s = Search(using=client, index=elasticIndex).query(q)[pageLowerLimit:pageUpperLimit]
#     response = s.execute()
#     print('Total hits found : ', response.hits.total)
#     totalResults = response.hits.total.value
#     paginator = esPaginator(totalResults = totalResults, perPage = 10)
#     posts = paginator.paginate(page)
#     search=get_results(response)
#     return totalResults, search, posts

# def eSearchRetrieveByID(idList = []):
#     client = Elasticsearch()
#     q = Q('ids',values=idList)
#     s = Search(using=client, index=elasticIndex).query(q)
#     response = s.execute()
#     print('Total hits found : ', response.hits.total)
#     search = get_results(response)
#     print(search)
#     return search
    




# def bulkUploadData():
#     client = Elasticsearch()
#     patentData = readDataFromindexJson(BULK_JSON_DATA_FILE)
#     helpers.bulk(client, patentData, index=elasticIndex)
    

# if _name_ == '_main_':
#     print("Opal guy details: \n",eSearch(firstName="opal"))
#     print("the first 20 Female gender details: \n", eSearch(gender="f"))

# def update(q):
#     c = Elasticsearch()
#     values = {"patentID": q['patentID'], "pid": q['pid'],"is_multiple": q['is_multiple'],"origreftext": q['origreftext'],"figid": q['figid'], "subfig": q['subfig'], 
#         "is_caption": q['is_caption'], "description": q['description'],  "aspect": q['aspect'], "object": q['objects']
#     }
#     response = c.index( index = 'search',doc_type = '_doc',body = values
#     )
#     if response['result'] == "created":
#         return True
#     else:
#         return False