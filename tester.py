import csv
import math
import time

def get_limits(path):
    excel = open(path,"r")
    dict_topic_limits ={}
    lines=excel.readlines()
    for line in lines:
        columns = line.split(',')
        dict_topic_limits[columns[1].strip('[""""]')]={"assessment":columns[0].strip(),"Lower_limit":int(columns[2].strip()),"Upper_limit":int(columns[3].strip())}
    return dict_topic_limits

def check_limits(topic_floor,topic_decimal,dict_topic_limits):
    print(dict_topic_limits)
    limit_fails=[]
    for key in topic_floor:
        if (topic_floor[key] < dict_topic_limits[key]["Lower_limit"]):
            limit_fails.append(key)
            print("TEST CANNOT BE CREATED because following topics have questions less than lower limit \n"+str(limit_fails))
        elif(topic_floor[key]>dict_topic_limits[key]["Upper_limit"]):
                print("running")
                topic_floor[key]=dict_topic_limits[key]["Upper_limit"]
                topic_decimal[key]=0.00
        
    return topic_floor,topic_decimal

def get_question_bank(path):
    excel = open(path,"r")
    # reader = csv.reader(excel, delimiter=',')
    array_question_bank = []
    lines = excel.readlines()
    for line in lines:     
        columns = line.split(',')
        array_question_bank.append({"QID": columns[0].strip(),"assessment":columns[1].strip(),"topic":columns[2].strip('[""""]'),"tag":columns[3].strip()})        
    return array_question_bank

def get_topic_count(array_question_bank,current_assesment):    
    dict_topic_count = {}
    for question in array_question_bank:    
            topic = question["topic"]
            qb_assesment = question["assessment"]
            if(qb_assesment == current_assesment):
                if topic in dict_topic_count :
                    dict_topic_count[topic] = dict_topic_count[topic] + 1   
                else:
                    dict_topic_count[topic] = 1
    return dict_topic_count
    
# extract question, calc ratio, total ques
def stats(dict_topic_count,total_questions,dict_topic_decimal):
    total_topic_question = 0
    # dict_topic_decimal={}
    for i in dict_topic_count: 
        total_topic_question = total_topic_question + dict_topic_count[i]
    # print (sum)
    ratio = 0.0
    for i in dict_topic_count:
        ratio = dict_topic_count[i]*total_questions/total_topic_question
        ceiling= math.ceil(ratio)
        decimal_value=round((ratio*10)%10)/10
        floor = math.floor(ratio)
        dict_topic_count[i] = floor
        if i in dict_topic_decimal:
            dict_topic_decimal[i] = decimal_value + dict_topic_decimal[i]
        else:
            dict_topic_decimal[i] = decimal_value
    return dict_topic_count,dict_topic_decimal

def print_dict(dict):
    for i in dict:
        print(i,dict[i])
    print("\n")


def brahmastra(topic_decimal, topic_floor):
    ques_sum=0
    for i in topic_floor:
        ques_sum = topic_floor[i]+ques_sum
    remaining_question = total_questions-ques_sum
    count = 0
    # dict_sorted = {value:key for key, value in topic_decimal.items()}

    for i in range(0,remaining_question):
        # if count == remaining_question:
        #     break
        topic = max(topic_decimal, key=topic_decimal.get)
        topic_floor[topic] = topic_floor[topic] + 1 
        topic_decimal[topic] = 0 if topic_floor[topic] - 1 < 0 else topic_floor[topic] - 1 
        count+=1
    return topic_decimal,topic_floor

def export_question(fw,test_count,question_bank,topic_question_distribution):
    for topic in topic_question_distribution:
        question_count = topic_question_distribution[topic] 
        for i in range(0,question_count):
            for question in question_bank:    
                if(question["topic"]==topic):
                    fw.write(str(question["QID"])+","+str(topic)+"\n")
                    print(str(question["QID"])+","+str(topic)+"\n")
                    question_bank.remove(question)
                    topic_question_distribution[topic] = topic_question_distribution[topic] - 1    
                    break
                

    


assessment_areas = ["Logical Reasoning/ Data Interpretation","Verbal Ability","Quantitative Aptitude"]
# question_bank = get_question_bank("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/QB.csv")
topic_limits=get_limits("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/limitss.csv")
question_bank = get_question_bank("QB.csv")
input_question_distribution = { assessment_areas[0]: 15, assessment_areas[1] : 30,assessment_areas[2]: 20}
decimal_bucket={assessment_areas[0]:{}, assessment_areas[1]:{ }, assessment_areas[2]:{},}
floor={}
test_count = 0
fw = open("Export"+str(time.time()),"w")
fw.write(str("Test")+str(test_count)+"\n")
for assessment in input_question_distribution :
    test_count+=1
    total_questions = input_question_distribution[assessment]
    topic_floor = get_topic_count(question_bank,assessment)
    topic_question_distribution,decimal_bucket[assessment] = stats(topic_floor,total_questions,decimal_bucket[assessment])
    check_limits(topic_floor,topic_limits)
    decimal_bucket[assessment],topic_question_distribution = brahmastra(decimal_bucket[assessment],topic_question_distribution)
    export_question(fw,test_count,question_bank,topic_question_distribution)
    print_dict(decimal_bucket)
    print_dict(topic_question_distribution)

fw.close()