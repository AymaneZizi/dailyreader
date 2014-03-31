from reader.models import *
from django.core.management.base import BaseCommand, CommandError
import os
from topia.termextract import extract



MAX_ARTICLES_IN_DATABASE=500
MIN_FREQUENCY_OF_KEY_WORD=0.05
NO_OF_PCATEGORY = 4



alphabets={'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'}

def is_not_alphanumeric(word):
    option=0
    returnValue=1
    while option<len(word):
        if  word[option] in alphabets:
            returnValue=0 
        option=option+1
    if len(word)<3:
        returnValue=1
    return returnValue
  

class Category_Training:
    def __init__(self):
        self.document_count=0
        self.word_count=0
        self.index=0
        self.name=""

class Key_Word_Training:
    def __init__(self):
        self.dict_count_document_present={} # contains category index: count
        self.dict_category_count={} # contains category index: total_count
        self.dict_frequency = {} # contains  index : dict_count_document_present/document_count_category
        self.dict_probability={} # contains  index : dict_category_count/document_count_category
        self.total_count=0
        self.name=""


def get_pcategory(category_name,list_p_category):
    for element in list_p_category:
        if element.name==category_name:
            return element
        
            
class Command(BaseCommand):
    def handle(self,*args, **options):
        lines=[]
        Features.objects.all().delete()
        PCategory.objects.all().delete()
        Article.objects.all().delete()
        with open(os.getcwd()+"/reader/management/commands/"+"training_data.csv","r") as file:
            lines=file.readlines()
        training_data=[]
        for line in lines:
            training_data.append(line.rsplit(",",1))
        print len(training_data)
        extractor=extract.TermExtractor()
        extractor.filter=extract.permissiveFilter
        #training_data=[]
        categories={}
        key_words= {}
        
        last_category_count=0
       
       
        # extracting keyword and category
        for element in training_data:
            description=element[0]
            category=element[1]
            
            if len(category.strip())==0:
                continue
            if not category in categories:
                new_category=Category_Training()
                new_category.index=last_category_count
                new_category.document_count=1
                new_category.name=category
                categories[category]=new_category
                last_category_count=last_category_count+1
            else:
                categories[category].document_count=categories[category].document_count+1
          
            key_word_for_desc=extractor(description)
            #print category
            for word in key_word_for_desc:
                if not word[0].lower() in key_words:
                    #print word[0]
                    new_key_word=Key_Word_Training()
                    key_words[word[0].lower()]=new_key_word
                # increasing the count
                category_object=categories[category]
                key_word_object = key_words[word[0].lower()]
                key_word_object.name=word[0].lower()
                key_for_category=str(category_object.index)    
                count_key_words=key_word_object.dict_category_count
                count_document_key_words=key_word_object.dict_count_document_present
                category_object.word_count=category_object.word_count+word[1]
                if  key_for_category in count_key_words:
                    #print word[1]
                    count_key_words[key_for_category]=count_key_words[key_for_category]+word[1]
                    count_document_key_words[key_for_category]=count_document_key_words[key_for_category]+1
                else:
                    #print word[1]
                    count_key_words[key_for_category]=word[1]
                    count_document_key_words[key_for_category]=1
                key_word_object.total_count=key_word_object.total_count+word[1]
                   
        
                  
        # refining the feature set
        # only keeping features    
        refined_features={}
        for word in key_words.keys():
            check_include_feature=0
            dict_count_category=key_words[word].dict_category_count
            dict_count_documents_category=key_words[word].dict_count_document_present
            for category in categories.keys():
                document_count= categories[category].document_count
                vocab_count = categories[category].word_count
                category_key=str(categories[category].index)
                probability_for_category=0
                frquency_for_category=0
                frquency_for_category=0
                total_count=key_words[word].total_count
               
                    
                if category_key in dict_count_category:
                    frquency_for_category=float(dict_count_documents_category[category_key])/document_count
                    probability_for_category=(float(dict_count_category[category_key]+1))/(2*vocab_count)
                    dict_probability=key_words[word].dict_probability
                    dict_probability[category_key]=probability_for_category
                    dict_frequency=key_words[word].dict_frequency
                    dict_frequency[category_key]=frquency_for_category
                else:
                    probability_for_category=float(1)/(2*vocab_count)
                    dict_probability=key_words[word].dict_probability
                    dict_probability[category_key]=probability_for_category
                    
                if frquency_for_category>MIN_FREQUENCY_OF_KEY_WORD:
                    check_include_feature=1
                  
                if check_include_feature:
                    if not (word.count('"')>0 or word.count("'")>0 or word.count("#")>0 or len(word.split(" "))>1 or is_not_alphanumeric(word)): 
                        refined_features[word]=key_words[word]
                         
        listCategoriesModel=[0]*NO_OF_PCATEGORY
        for key in  categories:
            pcategory=PCategory()
            pcategory.name=categories[key].name  
            listCategoriesModel[categories[key].index]=pcategory
 
         
        
        listFeaturesModel=[]
        print len(refined_features.keys())
        for key in refined_features:
            count=0
            for key_category in categories:
                category=categories[key_category]
                feature=Features()
                feature.name=key
                index = category.index
                
                feature.pcategory= listCategoriesModel[index]
                category_name=feature.pcategory.name
                
                #print category_name
                if str(index) in refined_features[key].dict_probability:
                    feature.probability=refined_features[key].dict_probability[str(index)]
                else:
                    feature.probability=0
                if  not feature.pcategory:
                    print index
                    print listCategoriesModel[index]    
                listFeaturesModel.append(feature)
 
        PCategory.objects.bulk_create(listCategoriesModel)
        pcategory_objects = PCategory.objects.all()
        
        for element in listFeaturesModel:
            category_name = element.pcategory.name
            #print category_name
            pcategory = get_pcategory(category_name,pcategory_objects )
            element.pcategory=pcategory
        pcategory=PCategory()
        pcategory.name=OTHER_KEY 
        pcategory.save()
        Features.objects.bulk_create(listFeaturesModel)
