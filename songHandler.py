# For authorisation we need to visit this website:
# https://accounts.spotify.com/en/authorize?response_type=token&redirect_uri=https:%2F%2Fdeveloper.spotify.com%2Fcallback&client_id=774b29d4f13844c495f206cafdad9c86&state=7hhgjh

# The dashboard can be found here:
# https://developer.spotify.com/dashboard/applications/d90119b7ca3e40d49d97dd2f45671aad

# Import relevant libraries
import os               # Import for curl access
#import json             # Import for json handling
import sys              # Import for argument access
import pandas as pd     # Import for dataframe capabilites

# This function handles the curl request
def get_json(playlistID, token):
    # Define the different url sections
    spotifyRequest = '"https://api.spotify.com/v1/playlists/'
    spotifyPresets = '/tracks?market=AU&fields=items(track.name%2C%20track.album.name)&limit=100&offset=0"'
    spotifyReturns = ' -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer '
    token = token + '"'

    # Concatenate the strings together
    spotifyFinal = spotifyRequest + playlistID + spotifyPresets + spotifyReturns + token

    # Run the http callback request
    return os.system('curl -X "GET" ' + spotifyFinal)

def handle_json(jsonReceived):
    # Take the respone of the callback request and convert it from json format
    subFrame = pd.read_json(jsonReceived)
    print(subFrame)

# Save the input arguments in variables for easy access
authToken = str(sys.argv[1])
# Define the path of the playlistIDs file
filePath = 'playlistIDs.txt'
# Open the file containing all the playlist ID's
idFile = open(filePath, 'r')
# Loop through the file and save each ID separately
IDs = idFile.readLines()
# Remove the newline characters from the array of strings
IDs = [i.replace('n', '') for i in IDs]
# Close the file now that we're done with it
idFile.close()

# TODO loop over playlist ID's and append the resulting list of track IDS to a globally stored datframe
for i in range(0, len(IDs)):
    jsonText = get_json(IDs[i], authToken)
    handle_json(jsonText)
