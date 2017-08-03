# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import Flask, render_template, request, redirect
import tweepy
import keys
from tweetClass import Tweet
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 \
as Features
from watson_developer_cloud import ConversationV1

import os
proxy = 'https://proxy.keybank.com:80'
os.environ['http_proxy'] = proxy 
os.environ['https_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['HTTPS_PROXY'] = proxy

app = Flask(__name__)
auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)

@app.route("/")
def hello_world():
    return "Welcome to KeyBank!"

@app.route("/<name>")
def welcome(name=None):
    tweetObjsArray = []
    public_tweets = api.mentions_timeline()

    for tweet in public_tweets:
        tweeturl = 'https://twitter.com/'+tweet.user.screen_name+'/status/'+str(tweet.id)
        tweetObj = Tweet(tweet.id,tweet.user.screen_name, tweet.text, tweeturl)
        tweetObjsArray.append(tweetObj)
    tweetArrayLen = len(tweetObjsArray)
	
    return render_template('tweets_v1.html', length=tweetArrayLen, tweetObjsArray=tweetObjsArray)

@app.route("/result/<tweet>", methods = ['GET', 'POST'])
def toneAnalyzer(tweet=None):
    tone_analyzer = ToneAnalyzerV3(
            username='228d1995-d986-4766-84aa-387e0d0978ef',
            password='mIjxH6u1o8sK',
            version='2016-02-11')

    text = tweet.split('::')[1].decode('utf-8')
    
    output = tone_analyzer.tone(text=text)    
    toneCatLength = len(output['document_tone']['tone_categories'])
    i = 0
    toneCategoryArray  = []
    toneCategoryName = []
    while i<toneCatLength:
        tonesLength = len(output['document_tone']['tone_categories'][i]['tones'])
        j=0
        category_name = output['document_tone']['tone_categories'][i]['category_name']
        tonesArray =  []
        while j<tonesLength:
            tone_Name =  output['document_tone']['tone_categories'][i]['tones'][j]['tone_name']
            score = output['document_tone']['tone_categories'][i]['tones'][j]['score']
            t = tone_Name + "," + str(score*100)
            j+=1
            tonesArray.append(t)
        toneCategoryName.append(category_name + ',' + str(j))
        i+=1
        toneCategoryArray.append(tonesArray)
        
        conversation = ConversationV1(
			username='44155676-ae90-45d0-b2af-d95b4ba0cba8',
			password='dXCx47VBwLPw',
			version='2017-05-26'
		)
		
	workspace_id = '14d740b5-4397-4860-bec9-38aaf91f4f7b'

	response = conversation.message(
		workspace_id=workspace_id,
		message_input={'text': text},
	)

	msg = response['output']['text'][0]
        
    
    return render_template('toneAnalysis_v1.html', tweet=tweet, toneCategoryArray=toneCategoryArray, toneCategoryName=toneCategoryName, length=toneCatLength, msg=msg)

@app.route("/posttweet/", methods=['POST'])
def tweetResponse():
    msg=request.form['msg']
    tweetId = request.form['id']
    username = request.form['username']
    name = request.form['name']
    
    replyText = '@' + username + ' ' + msg
    api.update_status(status=replyText, in_reply_to_status_id=tweetId)
    
    url='/'+name
    return redirect('url')

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
app.run(host='0.0.0.0', port=int(port))