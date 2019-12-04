import pymongo
import json
from bson.code import Code
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re
from collections import Counter
import numpy as np

emoji_dict = {
    "ð\x9f\x98\x8d": "\U0001F60D",
    "ð\x9f\x98\x86": "\U0001F606",
    "â\x9d¤": "\U00002764",
    "ð\x9f\x98®": "\U0001F62E",
    "ð\x9f\x98¢": "\U0001F622",
    "ð\x9f\x98\xa0": "\U0001F620",
    "ð\x9f\x91\x8d": "\U0001F44D",
    "ð\x9f\x91\x8e": "\U0001F44E",
}


def split_and_lower(s):
    return list(filter(None, re.split("[^a-z']", s.lower())))


def bar_plot_generator(title, bars, height):
    y_pos = np.arange(len(bars))
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.title(title)
    plt.show()
    plt.savefig("bar_" + title + ".png")


def word_cloud_generator(title, word_list):
    wordcloud = WordCloud(background_color="black", colormap="rainbow").generate(
        word_list
    )
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.title(title)
    plt.axis("off")
    plt.show()
    plt.savefig("cloud_" + title + ".png")


def sentiment_analysis_np(sender, s):
    with open("sentiment_dict.json") as template:
        template_dct = json.load(template)
    neg = template_dct["negative"]
    pos = template_dct["positive"]

    pos_list = list((Counter(s) & Counter(pos)).elements())
    neg_list = list((Counter(s) & Counter(neg)).elements())

    # Create bar plot
    height = [len(pos_list), len(neg_list)]
    bars = ("Positive", "Negative")
    bar_plot_generator(sender, bars, height)

    # Create word cloud
    word_cloud_generator(sender + " +", " ".join(pos_list))
    word_cloud_generator(sender + " -", " ".join(neg_list))


class FBManagement:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.db = self.client.fb
        self.fb = self.db.fb
        print("Finished init")

    # insert messages into db
    def insert_messages(self, filename):
        with open(filename) as template:
            template_dct = json.load(template)

        messages = template_dct["messages"]
        for message in messages:
            key = "content"
            if key in message:
                content = message[key]
                message[key] = split_and_lower(content)
                message["word_count"] = len(message[key])

        self.fb.insert_many(messages)
        print("Finished insert")

    # counts # of messages sent by each person
    def message_counts(self):
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
        """
        )

        reducer = Code(
            """
        function(key, values) {
            return Array.sum(values);
        };
        """
        )

        result = self.fb.map_reduce(mapper, reducer, "out")

        for doc in result.find():
            print(doc)

    # counts # of words sent by each person
    def word_counts(self):
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
        """
        )

        reducer = Code(
            """
        function(key, values) {
            return Array.sum(values);
        };
        """
        )

        result = self.fb.map_reduce(
            mapper, reducer, "out", query={"word_count": {"$gt": 0}}
        )

        for doc in result.find():
            print(doc)

    # returns most frequent reacts and frequency
    def frequent_reacts(self):
        mapper = Code(
            """
        function() {
            for (var idx = 0; idx < this.reactions.length; idx++) {
                var key = this.reactions[idx].reaction;
                var value = 1;
                emit(key, value);
            }
        };
        """
        )

        reducer = Code(
            """
        function(key, values) {
            return Array.sum(values);
        };
        """
        )

        result = self.fb.map_reduce(
            mapper, reducer, "out", query={"reactions": {"$exists": True}}
        )

        emojis = []
        count = []

        for doc in result.find():
            for k, v in doc.items():
                if k == "_id":
                    emojis.append(emoji_dict[v])
                else:
                    count.append(v)

        print(emojis, count)
        bar_plot_generator("Frequent Reacts", emojis, count)

    # sentiment analysis
    def sentiment_analysis(self):
        messages = self.fb.aggregate(
            [
                {"$match": {"word_count": {"$gt": 0}}},
                {"$unwind": "$content"},
                {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}},
            ]
        )

        for message in messages:
            sentiment_analysis_np(message["_id"], message["content"])

    # word cloud
    def word_cloud(self):
        messages = self.fb.aggregate(
            [
                {"$match": {"word_count": {"$gt": 0}}},
                {"$unwind": "$content"},
                {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}},
            ]
        )

        for m_arr in messages:
            message = " ".join(m_arr["content"])
            word_cloud_generator(m_arr["_id"], message)

    def find_all_messages(self):
        messages = self.fb.find()
        print("Number of records = " + str(messages.count()))
        for message in messages:
            print(message)

    def drop_messages(self):
        self.fb.drop()


if __name__ == "__main__":
    mongoDB = FBManagement()
    mongoDB.insert_messages("message_1.json")
    mongoDB.frequent_reacts()
    mongoDB.message_counts()
    mongoDB.word_counts()
    mongoDB.word_cloud()
    mongoDB.sentiment_analysis()
    mongoDB.drop_messages()
