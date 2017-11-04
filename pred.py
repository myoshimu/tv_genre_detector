#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__author__ = ('kmiki@google.com (Miki Katsuragi)')

import argparse
import pprint
import sys
from apiclient import sample_tools
from oauth2client import client


# Additional for Mecab
import pandas as pd
import MeCab
mt = MeCab.Tagger("-Owakati")


# Declare command-line flags.

argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('object_name',
    help='Full Google Storage path of csv data (ex bucket/object)')
argparser.add_argument('model_id',
    help='Model Id of your choosing to name trained model')
argparser.add_argument('project_id',
    help='Project Id of your Google Cloud Project')


#python pred.py "kmiki/master.txt" "genre-identifier" "starlit-granite-545"


def main(argv):

	service, flags = sample_tools.init(
		argv, 'prediction', 'v1.6', __doc__, __file__, parents=[argparser],
		scope=(
			'https://www.googleapis.com/auth/prediction',
			'https://www.googleapis.com/auth/devstorage.read_only'))
	try:
		# Get access to the Prediction API.
		papi = service.trainedmodels()
		tv = pd.read_csv('shiseido.csv')
		master = pd.read_csv('master.csv')
		#masterデータからジャンル生成
		df=pd.merge(tv,master,on='Program',how='left')

		for index,row in df.iterrows():
			#ジャンルがマスターデータにない場合予測
			if row.Genre != row.Genre:
				sample_text=mt.parse(row.Program)
				body = {'input': {'csvInstance': [sample_text]}}
				result = papi.predict(body=body, id=flags.model_id, project=flags.project_id).execute()
				genre="".join(result["outputLabel"])
				df.loc[index,'Genre'] = genre
				#print(df.ix[index].Genre)

	except client.AccessTokenRefreshError:
		print ('The credentials have been revoked or expired, please re-run '
		   'the application to re-authorize.')

	df.to_csv('output.csv')

if __name__ == '__main__':
  main(sys.argv)
