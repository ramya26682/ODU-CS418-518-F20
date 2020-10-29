from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch

def AdvancedSearch(patentID="", aspect=""):
    client = Elasticsearch()
    query_data = Q("bool", should=[Q("match", patentID=patentID),Q("match", aspect=aspect)],minimum_should_match=1)
    look = Search(using=client, index="search").query(query_data)[0:30]
    response = look.execute()
    search=get_results(response)
    return search

def get_results(response):
    results=[]
    for field in response:
        result_tuple = (field.patentID + ' ' + field.pid, field.is_multiple, field.patentID+ '-D0' +field.pid[2:]+'.png',field.aspect)
        results.append(result_tuple)
    return results

# if __name__ == '__main__':
#     print("Opal guy details: \n",eSearch(patentID="opal"))
#     print("the first 20 Female gender details: \n", eSearch(aspect="f"))


def Singlesearch(Q_text=""):
    client = Elasticsearch()
    query = MultiMatch(query=Q_text, fields=['patentID', 'pid','origreftext','description','aspect'], fuzziness='AUTO')
    look = Search(using=client, index='search').query(query)[0:30]
    response = look.execute()
    search=get_results(response)
    return search

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