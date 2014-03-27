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
  
  
def stem_word(word):
    if not (word.count('"')>0 or word.count("'")>0 or word.count("#")>0 or len(word.split(" "))>1 or is_not_alphanumeric(word)):\
        return word.lower()
    else:
        return "" 