import cfg
import sys
import irc.bot
import requests
import twitter
import random
import time
import pytumblr

#pip install python-twitter, pytumblr, irc

oauth = 'BQCBrKU0SZB9ct-7LmV0mPG2DXIb_uZyBPeo1XYwd1ro2NZgxSsDPYliW5ZkqTzTurqg6cu9Fwe0OTSMaIajvc4eJZCFx6YtaNk8bPGxXL2HcHrrjmVjGO_U568Gs5cTxWa1BYxYNqsEziFEpYXJ3FLDfeTqFXrgJzUNfEmrrfUwOrDvO725zFwxQUIiT4m4y4cbbxArJpwVdEhXbwTLus4okrwkiARE4CQnJFqBzLH08S5cy9IC0PqR97ccLVGlUR_MPN_5qtqlGdT-ZvgTh5D7Ez09WcqD3P6qb8K_ipM5sw'

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        ##VOTING
        global table
        global winner
        global skipskip
        self.skipskip=0
        #twitter INIT
        consumer_key = 'mj9lFkDA55M8yRfXRotDfiEt6'
        consumer_secret = 'WxVCkxLyDKIFgRW1Jm1TRf3Q7Ec7WS4Or7iSBOf8Fo9Pj4GvE8'
        access_token_key = '239036830-2NL2MhgnUZo69LRU2SLUECGgrH16EFgXSp9woUIU'
        access_token_secret = 'I3aEJSFGclBQgNupBpFF9zO6H98wQnghtpgrF4SQxGvUJ'
        self.tum_client = pytumblr.TumblrRestClient('7YCVkGyrnGNqAwuNKPtCnydkKBqKHnRs15yfITEakp9snPIObg')
        self.api = twitter.Api(
          consumer_key=consumer_key,
          consumer_secret=consumer_secret,
          access_token_key=access_token_key,
          access_token_secret=access_token_secret
        )
        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, token)], username, username)

    @staticmethod
    def first(x):
      return {
          1: 'I told a Hawaiian a joke that wasn\'t very funny',
          2: 'The tenth Fast and Furious movie should be called-',
          3: 'What is Romeo and Juliet\'s least favorite fruit?',
          4: 'I bought a shirt with corn printed all over it.',
          5: 'Any salad can be a Caesar salad-',
          6: 'When are plants awake?',
          7: 'I gave a flower to a cowboy-',
      }[x]
    @staticmethod
    def followup(x):
      return {
          1: 'He responded with a low \"ha\"',
          2: 'Fast 10: Your Seat belts',
          3: 'Can\'t-elope.',
          4: 'It was a crop top.',
          5: 'if you stab it enough.',
          6: 'At tree am',
          7: 'He said \'what in carnation?\'',
      }[x]

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        # print(e.arguments[0])
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        elif 'gonna' in e.arguments[0]:
            cmd = 'gonna'
            #print(cmd)
            self.insideJoke(e, cmd)
        elif 'going' in e.arguments[0]:
            cmd = 'going'
            #print(cmd)
            self.insideJoke(e, cmd)
        return

    def insideJoke(self, e, cmd):
        c = self.connection
        c.privmsg(self.channel, "bet you won't.")

    def do_command(self, e, cmd):
        c = self.connection

        #starts poll
        if cmd == "poll":
          self.table={e.arguments[0].split(' ')[1]: 0,
            e.arguments[0].split(' ')[2]:0,}

        #displays curret poll results
        elif cmd == "disppoll":
          for key,value in self.table.items():
            c.privmsg(self.channel, key+' score: '+str(value))

        #allows for voting increments by one
        elif cmd == "vote":
          for key,value in self.table.items():
            if(e.arguments[0].split(' ')[1]==key):
              self.table[key]+=1

        #ends poll
        elif cmd=="endpoll":
          dont_stop_me=[]
          dont_help_me=[]
          for key,value in self.table.items():
            list.append(dont_help_me,key)
            list.append(dont_stop_me,value)
          if(dont_stop_me[0]<dont_stop_me[1]):
            self.winner=dont_help_me[1]
            temp=dont_stop_me[1]
            dont_stop_me[1]=dont_stop_me[0]
            dont_stop_me[0]=temp
          else:
            self.winner=dont_help_me[0]
          self.winner.replace(" ","+")
          spot_url ='https://api.spotify.com/v1/search?q='
          spot_url+=self.winner
          spot_url+='&type=track'
          precursor='spotify%3Atrack%3A'
          headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + oauth,
          }
          rr = requests.get(spot_url, headers=headers).json()
          precursor+=rr['tracks']['items'][0]['id']
          spot_url='https://api.spotify.com/v1/users/1110278844/playlists/0wRv1nnXQKKib6TBd1dTY0/tracks?uris='+precursor
          rr = requests.post(spot_url, headers=headers)
          c.privmsg(self.channel, 'Poll is over and the song has been added to the People\'s choice playlist.')

        #checks playlist that's been created by the poll
        elif cmd == "peopleschoices":
            spot_url='https://api.spotify.com/v1/users/1110278844/playlists/0wRv1nnXQKKib6TBd1dTY0/tracks?limit=10'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + oauth,
            }
            rr = requests.get(spot_url, headers=headers).json()
            c.privmsg(self.channel, 'This playlist contains:')
            count=0
            while True:
                if(count>1):
                    break
                else:
                    c.privmsg(self.channel, rr['items'][0]['track']['name']+ ' by '+ rr['items'][0]['track']['artists'][0]['name'])
                    count += 1
                    
        #skip function
        elif cmd == "skip":
            self.skipskip+=1
            if(self.skipskip>4):
                spot_url = 'https://api.spotify.com/v1/me/player/next'
                headers = {
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + oauth,
                }
                rr = requests.post(spot_url, headers=headers)
                self.skipskip=0
        
        #tumblr post Lol
        elif cmd == "tumblr":
            tumblr=self.tum_client.posts('qualitymemetonite.tumblr.com', type='text')
            c.privmsg(self.channel, 'Recent post: '+' \"'+tumblr['posts'][0]['body']+'\"')
        
        # Funny Jokes haHaa
        elif cmd == "joke":
            intt=random.randint(1,7)
            c.privmsg(self.channel, self.first(intt))
            time.sleep(5)
            c.privmsg(self.channel, self.followup(intt))

        # Poll Twitter Api for last tweet (hardcode)
        elif cmd == "tweet":
            latest_tweet = self.api.GetUserTimeline(screen_name='aspceo')
            c.privmsg(self.channel, latest_tweet[0].text)

        # Poll the API to get current game.
        elif cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            if r['game'] is None:
                c.privmsg(self.channel, "There is no game currently being played.")
            else:
                c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])

        # provides streamer schedule
        elif cmd == "schedule":
            sched = ['Monday: 12PM - 8PM', 'Tuesday: 4PM - 7PM', 'Wednesday: 12PM - 5PM', 'Thursday: OFF', 'Friday: 10AM - 2PM', ]
            for i in sched:
                c.privmsg(self.channel, i)

        # favorite artist
        elif cmd == "fav_artist":
            # make request to spotify api
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            display_name = (r['display_name'])
            # print("DISPLAY " + display_name)
            spot_url = 'https://api.spotify.com/v1/me/top/artists?limit=5'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + oauth,
            }
            rr = requests.get(spot_url, headers=headers).json()
            artist = rr['items'][0]['name']
            message = display_name + ' favorite artist is ' + artist
            c.privmsg(self.channel, message)

        # get song that is now playing
        elif cmd == 'playing':
            spot_url = 'https://api.spotify.com/v1/me/player/currently-playing'
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + oauth,
            }
            r = requests.get(spot_url, headers=headers).json()
            #print(r)
            song = r['item']['name']
            artist = r['item']['artists'][0]['name']
            if r['is_playing'] == True and r['context']['type'] == 'playlist':
                c.privmsg(self.channel, song + ' - ' + artist + ' is now playing from: ' + r['context']['external_urls']['spotify'])
            elif r['is_playing'] == True:
                c.privmsg(self.channel, song + ' - ' + artist + ' is now playing')
            else:
                c.privmsg(self.channel, 'There is nothing currently being played.')

        elif cmd == 'help':
             c.privmsg(self.channel, 'poll, disspoll, endpoll, vote, peopleschoices, fav_artist, playing. tumblr, tweet, joke, game, title, schedule')

        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    bot = TwitchBot(cfg.username, cfg.client_id, cfg.token, cfg.channel)
    bot.start()

if __name__ == "__main__":
    main()
