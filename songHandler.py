# Readme
#--------------------------------------------------------------------
# songHandler.py is a python program to be run on a linux os which
# takes Spotify Playlist ID's (max length = 100 playlists) and sorts
# the top 100 songs from this list into a new playlist. When called,
# this program requires an 'access token' argument which can be
# obtained from one of the websites listed below. Enjoy
#                                       - Christian Murchie 20/12/18

# Relevant Web Resources
#--------------------------------------------------------------------
# For authorisation we need to visit this website:
# https://accounts.spotify.com/en/authorize?response_type=token&redirect_uri=https:%2F%2Fdeveloper.spotify.com%2Fcallback&client_id=774b29d4f13844c495f206cafdad9c86&state=7hhgjh

# The dashboard can be found here:
# https://developer.spotify.com/dashboard/applications/d90119b7ca3e40d49d97dd2f45671aad
#--------------------------------------------------------------------

# Import relevant libraries
#--------------------------------------------------------------------
import os               # Import for curl access
import re               # Import for string substitutions
import sys              # Import for argument access
import json             # Import for json handling
import pandas as pd     # Import for dataframe capabilites
from io import StringIO # Import for string input to dataframe
#--------------------------------------------------------------------

# Function Definitions
#--------------------------------------------------------------------

# This function handles the input argument and saves the required IDs
def initProgram():
    # Save the input arguments in variables for easy access
    token = str(sys.argv[1])

    # Define the path of the playlistIDs file
    filePath = 'playlistIDs.txt'
    # Open the file containing all the playlist ID's
    idFile = open(filePath, 'r')
    # Loop through the file and save each ID separately
    identifiers = idFile.readlines()
    # Close the file now that we're done with it
    idFile.close()
    # Remove the newline characters from the array of strings
    identifiers = [i.replace('\n', '') for i in IDs]

    # Return the authToken and IDs
    return token, identifiers

# This function handles the curl request
def get_json(playlistID, token):
    # Define the different url sections
    spotifyRequest = '"https://api.spotify.com/v1/playlists/'
    spotifyPresets = '/tracks?market=AU&fields=items.track.id&limit=100&offset=0"'
    spotifyReturns = ' -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer '
    token = token + '"'

    # Concatenate the strings together
    spotifyFinal = spotifyRequest + playlistID + spotifyPresets + spotifyReturns + token

    # Run the http callback request as a string
    return str(os.system('curl -X "GET" ' + spotifyFinal))

# This function handles the json input and places it in a data frame
def handle_json(jsonReceived):
    # Take the respone of the callback request and convert it from json format to a 'simple' dictionary
    data = json.load(jsonReceived)
    # Convert to a string for alteration
    data = str(data)

    # Shave off the unnecessary data for easy track reading
    data = re.sub('\{\'items\'\: \[', '', data)
    data = re.sub('\{\'track\'\: \{\'id\'\: \'', '', data)
    data = re.sub(' ', '', data)
    data = re.sub('\'}}', '', data)
    data = re.sub('\]\}', '', data)

    # Convert from a csv to a data frame
    subFrame = pd.read_csv(StringIO(data), header=None)
    subFrame = subFrame.transpose()

    # Return the data frame as a single column structure
    return subFrame

#--------------------------------------------------------------------

# The main program begins here
#--------------------------------------------------------------------

# Save the input argument and obtain the playlist IDs
authToken, IDs = initProgram()

# Create an empty array to store the dataframes
frameList = []

# Loop through every playlist ID
for i in range(0, len(IDs)):
    # Save the http callback response from the Spotify API for the selected ID
    jsonText = get_json(IDs[i], authToken)

    # Save the modified response dataframe in an array for later use
    frameList += handle_json(jsonText)

# Concatenate the dataframes together to form one big dataframe with all song occurances
trackFrame = pd.concat(frameList)

print(trackFrame)
