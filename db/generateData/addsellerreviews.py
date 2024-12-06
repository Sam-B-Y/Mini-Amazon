# '''
# Data generator CLEARS ALL DATA in existing CSVs (except Users) and regenerates it.
# '''

import csv
# from os import listdir, getcwd
# from os.path import isfile, join
# import pandas as pd
# import numpy as np
# import datetime
import random
from pprint import pprint

# reviews = pd.read_csv("../data/reviews.csv")

# reviews["comment"] = []

from openai import OpenAI
import pandas as pd
import os
api = None
# Replace 'your-api-key' with your OpenAI API key
client = OpenAI(
    api_key=api
)

reviews_df = pd.read_csv("db/data/reviews.csv")
reviews_df = reviews_df[2000:]
# reviews.iloc[0]["comment"] = "This is a test review"
r = {1: [], 2: [], 3: [], 4: [], 5: []}
n = 15

for i in r.keys():
    for j in range(n):
        messages = [
            {"role": "system", "content": "You are a helpful assistant who generates short, realistic, and generic seller reviews based on a given rating. Do not include any other text than the review, and do not include quotation marks in your response."},
        ]
        messages.append({"role": "user", "content": f"Generate a short, realistic, generic review for a seller based on the following rating: {i} stars. It should be less than 20 words."})
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages=messages,
            max_tokens=40
        )
        comment = response.choices[0].message.content.strip().replace('\"', '').replace(',', '')
        r[i].append(comment.replace(',', ''))

out = []

for i in reviews_df["rating"]:
    out.append(str(r[i][random.randint(0, n-1)]))
# print(out)
reviews_df["comment"] = out
reviews_df["product_id"] = ""
reviews_df.to_csv("sellerreviews.csv", index=False, quoting=csv.QUOTE_NONE, na_rep="")
    

# Specify the number of reviews you want to generate
# print(reviews_df["rating"])
# reviews = generate_generic_reviews(reviews_df["rating"])
# print(reviews)
# reviews_df["comment"] = reviews

# reviews_df.to_csv("db/data/reviews.csv", index=False)

# reviews.to_csv("../data/reviews.csv", index=False)