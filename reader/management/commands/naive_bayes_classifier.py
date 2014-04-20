from topia.termextract import extract
import re
MIN_FREQUENCY = 0.1
import unittest
import math

class Document:
    def __init__(self,text="",category_name=""):
        self.text = text
        self.category_name = category_name
    


class Key_Word():
    def __init__(self):
        self.dict_category_count={}
        self.dict_category_document_count={}
        self.dict_category_probability={}
        self.dict_category_frequency={}
        self.name=""

class Category():
    def __init__(self,index=0,document_count=0, vocab_count=0):
        self.document_count=document_count
        self.vocab_count = vocab_count
        self.index = index
        self.prior = 0.0 
        self.name = ""      

class TrainingData:
    
    def __get_category(self,document):
        extractor=extract.TermExtractor()
        extractor.filter=extract.permissiveFilter
        extracted_key_word=extractor(document.text)
        dict_category_value = {}
        # calculating likelihood for each category
        for word_object in extracted_key_word:
            word=word_object[0]
            count=word_object[1]
            if word in self.dict_refined_features:
                key_feature = self.dict_refined_features[word]
                for category_name in key_feature.dict_category_probability:
                    if category_name in dict_category_value:
                        dict_category_value[category_name]=dict_category_value[category_name]+count*math.log(key_feature.dict_category_probability[category_name],10)
                    else:
                        dict_category_value[category_name]=count*math.log(key_feature.dict_category_probability[category_name],10)
                
        # calculating prior
        for category_name in dict_category_value:
            dict_category_value[category_name]=dict_category_value[category_name]+math.log(self.dict_category[category_name].prior)
        max_value= -10000000000
        document_category_name=""
        # calculating max
        for category_name in dict_category_value:
            if dict_category_value[category_name]>=max_value:
                max_value=dict_category_value[category_name]
                document_category_name=category_name
        return document_category_name


    def get_category(self,document):
        return self.__get_category(document)
            
            
    
    def __init__(self,data=[]):
        self.list_training_data = []
        for element in data:
            self.list_training_data.append(element)
        self.dict_features={}
        self.dict_refined_features={}
        self.dict_category={}
        self.total_documents =0
        
    
    def get_all_categories(self):
        return self.dict_category
    
    def get_all_features(self):
        return self.dict_refined_features
    
    def __train_data(self):
        category_index = 0
        extractor=extract.TermExtractor()
        extractor.filter=extract.permissiveFilter
        for element in self.list_training_data:
            category_name = element.category_name
            text = element.text
            # extracting categories 
            if category_name in self.dict_category:
                category = self.dict_category[category_name]
                category.document_count = category.document_count+1
            else:
                category = Category()
                category.index=category_index
                category_index=category_index+1
                category.document_count = category.document_count+1
                self.dict_category[category_name]=category
                category.name=category_name

            # extracting features
            extracted_key_word=extractor(text)
            for element_word in extracted_key_word:
                word = element_word[0].lower()
                count_word = element_word[1]
                if word in self.dict_features and category_name in self.dict_features[word].dict_category_count:
                    key_word = self.dict_features[word]
                    key_word.dict_category_count[category_name]=key_word.dict_category_count[category_name]+count_word
                    key_word.dict_category_document_count[category_name]=key_word.dict_category_document_count[category_name]+1
                else:
                    key_word=Key_Word()
                    key_word.name=word
                    key_word.dict_category_document_count[category_name]=1
                    key_word.dict_category_count[category_name]=count_word
                    self.dict_features[word]=key_word
            # increasing total documents count
            self.total_documents=self.total_documents+1
        
        # refining the features set
        # refined_features =  key_feature(frequency in any category) >= MIN_FREQENCY
        # frequency is defined as (no of documents of a category in which key_feature is present) / (document_count_in_a_category) for a category
        for word in self.dict_features:
            key_feature = self.dict_features[word]
            for category_name in self.dict_category:
                category = self.dict_category[category_name]
                frequency=0
                if category_name in key_feature.dict_category_count:
                    document_count=category.document_count
                    documents_count_word_present=key_feature.dict_category_document_count[category_name]
                    frequency=float(documents_count_word_present)/document_count
                key_feature.dict_category_frequency[category_name]=frequency
                if frequency>=MIN_FREQUENCY and re.match("^[a-zA-Z0-9.]+$",word):
                    self.dict_refined_features[word]=key_feature
                    category.vocab_count = category.vocab_count+key_feature.dict_category_count[category_name]
                    
             
        #calculating probabilities for refined features 
        count_refined_features=len(self.dict_refined_features.keys())
        for word in self.dict_refined_features:
            key_feature = self.dict_refined_features[word]
            for category_name in self.dict_category:
                category = self.dict_category[category_name]
                vocab_count = category.vocab_count
                if category_name in key_feature.dict_category_count:
                    word_count = key_feature.dict_category_count[category_name]
                    key_feature.dict_category_probability[category_name]=float(word_count)/(vocab_count+count_refined_features)
                  
                else:      
                    key_feature.dict_category_probability[category_name] = float(1)/(vocab_count+count_refined_features)
            
        # calculating pior
        for category in self.dict_category:
            self.dict_category[category].prior= float(self.dict_category[category].document_count)/self.total_documents
          
    
    def train_data(self):
        self.__train_data()

    def add_document(self,document):
        self.list_training_data.append(document)
        

class NaiveBayesTests(unittest.TestCase):
    def test_one(self):
        print "checking key word extraction"
        document1 = Document("This category contains indian metros : delhi, chennai, mumbai and kolkata","India")
        document2 = Document("Delhi is in north","India")
        document3 = Document("Chennai is in south","India")
        document4 = Document("Kolkata is in east","India")
        document5 = Document("Mumbai is in west, not in north","India")
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
        training.add_document(document4)
        training.add_document(document5)
        training.train_data()
        self.failUnless(abs(training.dict_refined_features["mumbai"].dict_category_frequency["India"]-0.4)<1e-6 and
                        abs(training.dict_refined_features["category"].dict_category_frequency["India"]-0.2)<1e-6)
    def test_two(self):
        print "checking probability calculation"
        document1 = Document("This category contains indian metros : delhi, chennai, mumbai and kolkata","India")
        document2 = Document("Delhi is in north","India")
        document3 = Document("Chennai is in south","India")
        document4 = Document("Kolkata is in east","India")
        document5 = Document("Mumbai is in west, not in north","India")
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
        training.add_document(document4)
        training.add_document(document5)
        training.train_data()
        self.failUnless(abs(training.dict_refined_features["mumbai"].dict_category_probability["India"]-0.1)<1e-6 and
                        abs(training.dict_refined_features["category"].dict_category_probability["India"]-0.05)<1e-6)

    def test_three(self):
        print "checking probability calculation"
        document1 = Document("delhi india kolkata","India")
        document2 = Document("chennai india mumbai","India")
        document3 = Document("Newyork chicago","US")
        document4 = Document("boston philadephia","US")
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
        training.add_document(document4)
        training.train_data()
        self.failUnless(abs(training.dict_refined_features["mumbai"].dict_category_probability["India"]-0.06666666666666667)<1e-6 and
                        abs(training.dict_refined_features["mumbai"].dict_category_probability["US"]- 0.07692307692307693)<1e-6)
    def test_four(self):
        print "checking probability calculation"
        document1 = Document("delhi india kolkata","India")
        document2 = Document("chennai india mumbai","India")
        document3 = Document("Newyork chicago","US")
        document4 = Document("boston philadephia","US")
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
        training.add_document(document4)
        training.train_data()
        self.failUnless(abs(training.dict_refined_features["mumbai"].dict_category_probability["India"]-0.06666666666666667)<=1e-6 and
                        abs(training.dict_refined_features["mumbai"].dict_category_probability["US"]- 0.07692307692307693)<=1e-6)

    def test_five(self):
        print "checking prior calculation"
        document1 = Document("delhi india kolkata","India")
        document2 = Document("chennai india mumbai","India")
        document3 = Document("Newyork chicago","US")
    
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
    
        training.train_data()
        self.failUnless(abs(training.dict_category["India"].prior-0.666666666667)<1e-6 and
                        abs(training.dict_category["US"].prior-0.33333333333333)<1e-6)

    def test_six(self):
        print "checking prior calculation"
        document1 = Document("delhi india kolkata","India")
        document2 = Document("chennai india mumbai","India")
        document3 = Document("delhi india mumbai","India")
        document4 = Document("Newyork chicago","US")
        document5 = Document("delhi is in india","")
        training = TrainingData()
        training.add_document(document1)
        training.add_document(document2)
        training.add_document(document3)
        training.add_document(document4)
        training.train_data()
        self.failUnless(training.get_category(document5)=="India")

def main():
    unittest.main()

if __name__ == '__main__':
    main()
        
        
             
            
