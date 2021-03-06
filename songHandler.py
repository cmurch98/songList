# Readme
# --------------------------------------------------------------------
# songHandler.py is a python program to be run on a linux os which
# takes Spotify Playlist ID's (max length = 100 playlists) and sorts
# the top 100 songs from this list into a new playlist. When called,
# this program requires an 'access token' argument which can be
# obtained from one of the websites listed below. Enjoy
#                                       - Christian Murchie 20/12/18
# --------------------------------------------------------------------
# Relevant Web Resources
# --------------------------------------------------------------------
# For authorisation we need to visit this website:
# https://accounts.spotify.com/en/authorize
# The dashboard can be found here:
# https://developer.spotify.com/dashboard/applications/
# --------------------------------------------------------------------
# Import relevant libraries
# --------------------------------------------------------------------
import os               # Import for curl access
import re               # Import for string substitutions
import sys              # Import for argument access
import json             # Import for json handling
import numpy as np      # Import for sorting
import pandas as pd     # Import for dataframe capabilites
from io import StringIO  # Import for string input to dataframe
# --------------------------------------------------------------------
# Function Definitions
# --------------------------------------------------------------------
# This function handles the input argument and saves the required IDs
def init_program():
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
    identifiers = [i.replace('\n', '') for i in identifiers]
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
    spotifyFinal = spotifyRequest + playlistID + \
        spotifyPresets + spotifyReturns + token

    # Run the http callback request and save output in response.txt
    os.system('curl -X "GET" ' + spotifyFinal + ' -o response.txt')

    # Open response.txt and save the files in a variable
    responseFile = open('response.txt', 'r')
    response = responseFile.readlines()
    # Close the file to save memory
    responseFile.close()
    # Delete the file for iterative measures
    os.remove('response.txt')
    # Remove the newline characters from the array of strings
    response = [i.replace('\n', '') for i in response]

    return response

# This function handles the json input and places it in a data frame
def handle_json(jsonReceived):
    # Take the respone of the callback request and convert it from json format to a 'simple' dictionary
    data = json.loads("".join(jsonReceived))
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

# This function sorts the dataframe into decending order for song repeats
def track_sorter(dataframe):
    # Sort the 0th column for song counting
    sortedFrame = dataframe[0].value_counts()
    # for i in range(0,100):
    topOneHundred = sortedFrame[0:100]

    return topOneHundred

# This function adds the
def track_adder(songs, DESTINATIONPLAYLIST, token):
    # Define the different url sections
    spotifyInit = 'curl -X "POST" "https://api.spotify.com/v1/playlists/'
    spotifyPostInit = '/tracks?position=0&uris='
    spotifyRequest1 = spotifyInit + DESTINATIONPLAYLIST + spotifyPostInit
    spotifyRequest2 = spotifyInit + DESTINATIONPLAYLIST + spotifyPostInit

    # Loop through each track ID
    for i in range(0, 50):
        # Concatenate each track uri to the request string
        spotifyRequest1 += 'spotify%3Atrack%3A' + songs[i]
        if i != 49:
            # If it's not the last track add a comma
            spotifyRequest1 += '%2C'
        else:
            # On the last track, close the string
            spotifyRequest1 += '"'

    # Loop through each track ID
    for i in range(51, 100):
        # Concatenate each track uri to the request string
        spotifyRequest2 += 'spotify%3Atrack%3A' + songs[i]
        if i != 99:
            # If it's not the last track add a comma
            spotifyRequest2 += '%2C'
        else:
            # On the last track, close the string
            spotifyRequest2 += '"'

    # Add on further request requirements
    spotifyContext = ' -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer'
    spotifyRequest1 += spotifyContext
    spotifyRequest2 += spotifyContext

    # Add the token with public and private playlist requests
    spotifyToken = ' ' + token + '"'
    spotifyRequest1 += spotifyToken
    spotifyRequest2 += spotifyToken

    # Call the curl request
    print(spotifyRequest1)
    os.system(spotifyRequest1)
    print(spotifyRequest2)
    os.system(spotifyRequest2)

# --------------------------------------------------------------------
# The main program begins here
# --------------------------------------------------------------------
# This is the playlist ID for the 'output playlist'
OUTPUTPLAYLIST = '6NqAZvfAs36JBO3YAvUCyw'

# Save the input argument and obtain the playlist IDs
authToken, IDs = init_program()

# Create an empty array to store the dataframes
frameArray = []

# Loop through every playlist ID
for i in range(0, len(IDs)):
    # Save the http callback response from the Spotify API for the selected ID
    jsonText = get_json(IDs[i], authToken)

    # Save the modified response dataframe in an array for later use
    frameArray += [handle_json(jsonText)]

# Concatenate the dataframes together to form one big dataframe with all song occurances
trackFrame = pd.concat(frameArray)
# print(trackFrame.to_string())

# Sort the songs by frequency into a new 100 x 1 dataframe
sortedFrame = track_sorter(trackFrame).to_string()
sortedFrame = "".join(sortedFrame)
sortedFrame = re.sub('    \w{1}', '', sortedFrame)
sortedFrame = sortedFrame.split('\n')

# Adds the songs to the selected playlist, change or clear the playlist every run
track_adder(sortedFrame, OUTPUTPLAYLIST, authToken)
