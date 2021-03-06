import json
import requests
import urllib.request
from Preprint import Preprint

# Helper function to download a file from a URL
def download( url, localFile ):
	
	response = urllib.request.urlretrieve(url, localFile)

# Generic function to send a query to the API
def queryAPI( url, headers ):

	response = requests.get(url, headers=headers)
	return response

# Helper function to extract and decode JSON from API responses
def getJSON( response ):

	json_object = json.loads(response.content.decode('utf-8'))
	return json_object

# Helper function to parse JSON response and look for identifier data
def parseIdentifier ( jsonData, preprint ):

	num_elements = len( jsonData['data'] )
	for j in range( num_elements ):
		data = jsonData['data'][j]
		preprint.parseIdentifierData( data )

# Function to loop over all preprints in the response and parse their data
def parsePreprints( preprints, json_object, headers, verbose=True ):

	# Loop over all the response preprints
	for i in range( len(json_object['data']) ):
	
		# Response is comprised of Relationships, Links, and Attributes
		# Here we seperate them out of the response
		rel = json_object['data'][i]['relationships']
		attr = json_object['data'][i]['attributes']

		# We're going to ignore 'links' as we can construct these ourselves
		# from the id - API provides us with html, download, and doi links
		# links = json_object['data'][i]['links']
		
		# Also need to extract scalar values like id and construct the download link
		id = json_object['data'][i]['id']
		html_link = "https://engrxiv.org/" + id 
		download_link = "https://engrxiv.org/" + id + "/download"
		if ( verbose ): print( "Working on preprint ", len(preprints)+1 ) # should be 1 when len=0, thus the +1
		
		# Create a Preprint object to store all the information on this preprint
		preprint = Preprint()

		# Add the id and download_link values to our object
		preprint.setScalars( id, html_link, download_link )

		# Parse the Attributes data for this preprint
		preprint.parseAttrData( attr )

		# The Relationships data has links to more information
		# Use our helper function to extract those links and put them in our preprint object
		preprint.parseRelData( rel )

		# Now that we have the identifiers link (from the Relationships data), send it back to the API
		# to get the Identifier JSON and extract the actual DOI identifier
		response2 = queryAPI( preprint.identifiersLink, headers )
		if response2.status_code == 200:
			json_object2 = getJSON( response2 )
			parseIdentifier( json_object2, preprint )
		else:
			print( "Error parsing Identifier Link, HTTP status code is: ", response2.status_code )

		# Do the same with the citation link to get all the authors
		response2 = queryAPI( preprint.citationLink, headers )
		if response2.status_code == 200:
			json_object2 = getJSON( response2 )
		else:
			print( "Error parsing Citation Link, HTTP status code is: ", response2.status_code )

		# Add the current preprint to our list of preprints
		preprints.append( preprint )

