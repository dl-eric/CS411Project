import pymongo
import json
from bson.code import Code
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re
from collections import Counter
import numpy as np

emoji_dict = {
    'ð\x9f\x98\x8d': '\U0001F60D',
    'ð\x9f\x98\x86': '\U0001F606',
    'â\x9d¤': '\U00002764',
    'ð\x9f\x98®': '\U0001F62E',
    'ð\x9f\x98¢': '\U0001F622',
    'ð\x9f\x98\xa0': '\U0001F620',
    'ð\x9f\x91\x8d': '\U0001F44D',
    'ð\x9f\x91\x8e': '\U0001F44E'
}

def split_and_lower(s): 
    return list(filter(None, re.split("[^a-z']", s.lower())))

def bar_plot_generator(title, bars, height):
    y_pos = np.arange(len(bars))
    fig = plt.figure()
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.title(title)
    fig.savefig(title + ' bar' + '.png')
    #plt.clt()

def word_cloud_generator(title, word_list):
    if (len(word_list) > 0):
        wordcloud = WordCloud(background_color="black", colormap="rainbow").generate(word_list)
        fig = plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(title)
        plt.axis("off")
        fig.savefig(title + ' wc' + '.png')
    #plt.clt()
    
def sentiment_analysis_np(userid, friendid, sender, s):
    with open('sentiment_dict.json') as template:
        template_dct = json.load(template)
    neg = template_dct['negative']
    pos = template_dct['positive']
    
    pos_list = list((Counter(s) & Counter(pos)).elements())
    neg_list = list((Counter(s) & Counter(neg)).elements())
    
    # Create bar plot
    height = [len(pos_list), len(neg_list)]
    bars = ('Positive', 'Negative')
    bar_plot_generator(str(userid)+ str(friendid) + sender, bars, height)

    # Create word cloud
    word_cloud_generator(str(userid)+ str(friendid) + sender + ' +', " ".join(pos_list))
    word_cloud_generator(str(userid)+ str(friendid) + sender + ' -', " ".join(neg_list))
    
def split_and_lower(s): 
    return list(filter(None, re.split("[^a-z']", s.lower())))

class FBManagement:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.db = self.client.fb
        self.fb = self.db.fb
        print('Finished init')
    
    # insert messages into db
    def insert_file(self, userid, friendid, fileid, filename):
        with open(filename) as template:
            template_dct = json.load(template)
        
        messages = template_dct['messages']
        
        for message in messages:
            key = 'content'
            if ((key in message) and (message['type'] == 'Generic')):
                content = message[key]
                message[key] = split_and_lower(content)
                message['word_count'] = len(message[key])
                message['userid'] = userid
                message['friendid'] = friendid
                message['fileid'] = fileid
        
        self.fb.insert_many(messages)
        
        print('Finished insert')
    
    def remove_user(self, userid):
        self.fb.remove( { 'userid': userid } )
        
    def remove_friend(self, userid, friendid):
        self.fb.remove( {'$and': [{ 'userid': userid }, { 'friendid' : friendid }] } )
        
    def remove_file(self, userid, friendid, fileid):
        self.fb.remove( {'$and': [{'userid': userid }, { 'friendid' : friendid }, { 'fileid' : fileid }] } )
        
    # counts # of messages sent by each person
    def message_counts(self, userid, friendid):
        mapper = Code(
        """
        function() {
            // derived from lecture
            for (var idx = 0; idx < this.sender_name.length; idx++) {
                var key = this.sender_name;
                var value = 1;
                emit(key, value);
            }
        };
        """)

        reducer = Code(
        """
        function(key, values) {
            return Array.sum(values);
        };
        """)

        result = self.fb.map_reduce(mapper, reducer, "out", query = {'$and': [{'userid': userid }, { 'friendid' : friendid }]})

        for doc in result.find():
            print(doc)
            
    # counts # of words sent by each person
    def word_counts(self, userid, friendid):
        mapper = Code(
        """
        function() {
            // derived from lecture
            for (var idx = 0; idx < this.sender_name.length; idx++) {
                var key = this.sender_name;
                var value = this.word_count;
                emit(key, value);
            }
        };
        """)

        reducer = Code(
        """
        function(key, values) {
            return Array.sum(values);
        };
        """)
        
        result = self.fb.map_reduce(mapper, reducer, "out", query = {'$and': [{'word_count': { "$gt": 0 }}, {'userid': userid }, { 'friendid' : friendid }]})
        
        for doc in result.find():
            print(doc)
    
    # returns most frequent reacts and frequency
    def frequent_reacts(self, userid, friendid):
        mapper = Code(
        """
        function() {
            for (var idx = 0; idx < this.reactions.length; idx++) {
                var key = this.reactions[idx].reaction;
                var value = 1;
                emit(key, value);
            }
        };
        """)

        reducer = Code(
        """
        function(key, values) {
            return Array.sum(values);
        };
        """)

        result = self.fb.map_reduce(mapper, reducer, "out", query = {'$and': [{ 'userid': userid }, { 'friendid' : friendid }, {'reactions': { "$exists": True }}]})
        
        emojis = []
        count = []
        
        for doc in result.find():
            for k, v in doc.items():
                if (k == '_id'):
                    emojis.append(emoji_dict[v])
                else:
                    count.append(v)
        
        print(emojis, count)
        bar_plot_generator("Frequent Reacts", emojis, count)
                    
    # sentiment analysis
    def sentiment_analysis(self, userid, friendid):
        messages = self.fb.aggregate(
            [{"$match": {'$and': [{'userid': userid }, { 'friendid' : friendid }, {'word_count': { "$gt": 0 }}]}},
            {"$unwind":"$content"},
            {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}}]
        )
        
        for message in messages:
            sentiment_analysis_np(userid, friendid, message['_id'], message['content'])
    
    # word cloud
    def word_cloud(self, userid, friendid):
        messages = self.fb.aggregate(
            [{"$match": {'$and': [{'userid': userid }, { 'friendid' : friendid }, {'word_count': { "$gt": 0 }}]}},
            {"$unwind":"$content"},
            {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}}]
        )
        
        for m_arr in messages:
            message = " ".join(m_arr['content'])
            word_cloud_generator(str(userid) + str(friendid) + m_arr['_id'], message)
            
    def find_messages_between(self, userid, friendid):
        messages = self.fb.find( {'$and': [{ 'userid': userid }, { 'friendid' : friendid }] } )
        
        print("Number of records = " + str(messages.count()))
        for message in messages:
            print(message)
            
    def find_messages_in_file(self, userid, friendid, fileid):
        messages = self.fb.find( {'$and': [{ 'userid': userid }, { 'friendid' : friendid }, { 'fileid': fileid }] } )
        print("Number of records = " + str(messages.count()))
        for message in messages:
            print(message)

    def drop_messages(self):
        self.fb.drop()
                
if __name__ == "__main__":
    mongoDB = FBManagement()
    mongoDB.insert_file(1, 1, 1, 'message_1.json')
    mongoDB.message_counts(1, 1)
    mongoDB.word_counts(1, 1)
    mongoDB.frequent_reacts(1, 1)
    mongoDB.word_cloud(1, 1)
    mongoDB.sentiment_analysis(1, 1)
    
    mongoDB.insert_file(1, 2, 1, 'message_2.json')
    mongoDB.message_counts(1, 2)
    mongoDB.word_counts(1, 2)
    mongoDB.frequent_reacts(1, 2)
    mongoDB.word_cloud(1, 2)
    mongoDB.sentiment_analysis(1, 2)
    mongoDB.drop_messages()