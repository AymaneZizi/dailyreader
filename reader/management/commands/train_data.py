from reader.models import *
from django.core.management.base import BaseCommand, CommandError
import os
from topia.termextract import extract
import naive_bayes_classifier
from constants.app_constants import *


def get_pcategory(category_name,pcategory_objects):
    other_category = None
    category = None
    for element in pcategory_objects:
        if element.name == category_name:
            category= element
        if element.name== "OTHER_KEY":
            other_category=element
    
    if category:
        return category
    else:
        return other_category
        
    


class Command(BaseCommand):
    def handle(self,*args, **options):
        lines_documents=[]
        # delete features, pcategory and articles
        Features.objects.all().delete()
        PCategory.objects.all().delete()
        Article.objects.all().delete()
        with open(os.getcwd()+"/reader/management/commands/"+"training_data.csv","r") as file:
            lines=file.readlines()
        list_training_data=[]
        
        for line in lines:
            data=line.rsplit(",",1)
            document=naive_bayes_classifier.Document()
            document.text=data[0]
            document.category_name=data[1]
            list_training_data.append(document)
         
        training = naive_bayes_classifier.TrainingData(list_training_data)     
        training.train_data()
            
        dict_categories = training.get_all_categories()
        
        dict_features = training.get_all_features()
        
                         
        listCategoriesModel=[0]*NO_OF_PCATEGORY
        for key in  dict_categories:
            pcategory=PCategory()
            pcategory.name=dict_categories[key].name  
            listCategoriesModel[dict_categories[key].index]=pcategory
 
         
        
        listFeaturesModel=[]
       
        for key in dict_features:
            for key_category in dict_categories:
                category=dict_categories[key_category]
                feature=Features()
                feature.name=key
                index = category.index
                
                feature.pcategory= listCategoriesModel[index]
                category_name=feature.pcategory.name
                
                #print category_name
                if str(category_name) in dict_features[key].dict_category_probability:
                    feature.probability=dict_features[key].dict_category_probability[str(category_name)]
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
