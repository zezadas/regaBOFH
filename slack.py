#!/usr/bin/env python3
#template from: https://gist.github.com/bboe/0306fa90271ffc4c21add661d98a81f3
#API List: https://api.slack.com/methods

"""Set retention on slack conversations to 400 days.
Usage: ./set_retention.py [--perform] --token SLACK_TOKEN
The `--perform` flag is necessary to actually perform the action.
Due to the fact that `conversations.setToken` is not part of the public API
the slack legacy token concept will not work. To obtain the API token,
open up slack in the browser and observe networking traffic while performing
a few POST actions on the desired slack workspace. The data field to the POST
message should contain a token beginning with `xoxs-`; that's your token.
"""
import argparse
import os
import sys
import time

import slacker
from requests import HTTPError, ReadTimeout, Session
import requests
import pickle
import os.path

dry_run=False

def main():
    parser = argparse.ArgumentParser(
        description='F*** BOFH, Get Money',
        usage='%(prog)s [--token]')
    parser.add_argument('--dry-run', action="store_true",
                        help='Do not execute actions that modify content. Just mock it.')
    parser.add_argument('--token', help=(
        'The token used to connect to slack. This value can also be passed via'
        'the SLACK_TOKEN environment variable.'))
    parser.add_argument('--cookies', help=(
        'The cookies present on your browser used to connect to slack. This value can also be passed via'
        'the SLACK_COOKIES environment variable.'))

    args = parser.parse_args()
    
    global dry_run
    if args.dry_run:
        dry_run = True
        
        
    token = args.token or os.getenv('SLACK_TOKEN')
    if not token:
        sys.stderr.write('Either the argument --token or the environment '
                         'variable SLACK_TOKEN must be provided\n')
        return 1


    cookies = args.cookies or os.getenv('SLACK_COOKIES')
    if not cookies:
        sys.stderr.write('Either the argument --cookies or the environment '
                         'variable SLACK_COOKIES must be provided\n')
        return 1

    cj = requests.utils.cookiejar_from_dict(dict(p.split('=') for p in cookies.split('; ')))
    with Session() as session:
        session.cookies = cj
        
        slack = slacker.Slacker(token, session=session)
        
        userzadas=get_user_me(slack)
        WHOAMI=userzadas['user_id']
        print ("\nI'm user "+WHOAMI+"\n")
        
        try:
            #cache this for future uses
            #list users on workspace
            sys.stdout.write("\r" + "> Fetching Users")
            if os.path.isfile('./users.rick') == True:
                by_id = pickle.load( open( "users.rick", "rb" ) )
            else:
                by_id = users(slack)
                pickle.dump( by_id, open( "users.rick", "wb" ) )
            #print (by_id)
            sys.stdout.flush()
            sys.stdout.write("\r" + "> Users fetched \n")
            
            #list private conversations that are not empty
            #cache this also.
            sys.stdout.write("\r" + "> Fetching private conversations")
            if os.path.isfile('./private_conversations_list.rick') == True:
                private_conversationszadas = pickle.load( open( "./private_conversations_list.rick", "rb" ) )
            else:
                private_conversationszadas=get_private_IM_channel(slack, by_id)
                pickle.dump( private_conversationszadas, open( "./private_conversations_list.rick", "wb" ) )
            sys.stdout.flush()
            sys.stdout.write("\r" + "> Private conversations fetched \n")
            
            print ("\nUsers:")
            for user_chat in private_conversationszadas:
                print (" - " + user_chat)
            
            #print ("List of conversation retrieved\n")
            
            conversations_choosen=input("\n> Write the nicks separated by ',' that you wish to delete the conversations.\n>> ")
            conversation_list=conversations_choosen.split(",")
            print("")
        
            filtered_conversation_list=[]
            for i in conversation_list:
                a=i.strip()
                
                if a=="":
                    continue
                
                if a in private_conversationszadas.keys():
                    filtered_conversation_list.append(a)
                else:
                    print ("ERROR: User "+a+" is not valid")
                #print (filtered_conversation_list)
        
        
            for nickname in filtered_conversation_list:
                channelzadas=private_conversationszadas[nickname]
                sys.stdout.write("\r" + "> Fetching chat history for "+channelzadas)
                
                #backup your chat as pickle
                if os.path.isfile('./'+channelzadas+'_'+nickname+'_private_conversation.rick') == True:
                    channel_messages = pickle.load( open( './'+channelzadas+'_'+nickname+'_private_conversation.rick', "rb" ) )
                else:
                    channel_messages=get_private_IM_messages_from_channel(slack, channelzadas)
                    pickle.dump( channel_messages, open( './'+channelzadas+'_'+nickname+'_private_conversation.rick', "wb" ) )
                sys.stdout.flush()
                sys.stdout.write("\r" + "> Chat history for "+channelzadas+" fetched \n\n")
            
            
                #perform messages deletion
                #List own messages - that are the ones we can delete ;)
                sys.stdout.write("\r" + "> Deleting messages for "+nickname+'\n')
                delete_messages=input(">>>> Are you sure (y/n)\n>> ")
                if delete_messages != "y":
                    print (">>>> aborted by user")
                    raise
                deleted_count=0
                max_chars=37
                for msgs in channel_messages:
                    #print (channel_messages[msgs])
                    if 'user' in channel_messages[msgs].keys():
                        if channel_messages[msgs]['user']==WHOAMI:
                            #print (channel_messages[msgs])
                            deleted_count+=1
                            sys.stdout.flush()
                            xxx=channel_messages[msgs]['text'].strip().replace("\n","<LN>")[0:max_chars-3]
                            xxx+="..."
                            if len(xxx)<max_chars:
                                xxx+=" "*(max_chars-len(xxx))
                            sys.stdout.write("\r" + xxx)
                            if dry_run:
                                time.sleep(0.1)
                            delete_private_message(slack, channelzadas, channel_messages[msgs]['ts'])
                sys.stdout.flush()
                if deleted_count == 0:
                    xxx = '> Messages with "+nickname+" do not contain messages of yours'
                    if len(xxx)<max_chars:
                        xxx+=" "*(max_chars-len(xxx))
                    sys.stdout.write("\r" + xxx+'\n\n')
                    
                else:
                    sys.stdout.write("\r" + "> Messages deleted for "+nickname+". Total Deleted: "+str(deleted_count)+"\n\n")
        except:
            sys.stdout.flush()
            sys.stdout.write("\r" + "> Messages could not be retrived or something happened\n")                    
                
        try:
            sys.stdout.write("\r" + "> Fetching reactions and delete them\n")
            delete_reactions=input(">>>> Are you sure (y/n)\n>> ")
            max_chars=37
            if delete_reactions != "y":
                print (">>>> aborted by user")
                raise
            for reaction_list in get_reactions_list(slack,WHOAMI):
                for reaction in reaction_list['message']['reactions']:
                    if WHOAMI in reaction['users']:
                        sys.stdout.flush()
                        xxx=('react '+reaction['name']+'on ' + reaction_list['channel']).strip().replace("\n","<LN>")[0:max_chars-3]
                        xxx+="..."
                        if len(xxx)<max_chars:
                            xxx+=" "*(max_chars-len(xxx))
                        sys.stdout.write("\r" + xxx)
                        if dry_run:
                            time.sleep(0.1)
                        delete_reaction(slack,reaction['name'],reaction_list['channel'],reaction_list['message']['ts'])
            sys.stdout.flush()
            xxx='> Reactions Deleted'
            if len(xxx)<max_chars:
                xxx+=" "*(max_chars-len(xxx))
            sys.stdout.write("\r" + xxx+'\n')
        except:
            sys.stdout.flush()
            sys.stdout.write("\r" + "> Reactions could not be retrived or something happened\n")
        print("")
        
        try:
            size=0
            for file_info in get_file_list(slack,None,WHOAMI):
                #print(file_info)
                size += file_info['size']
                delete_file(slack,file_info['id'])
                
            print (">> Your files on workspace will ocupy about "+str(size/1e6).split('.')[0]+"MB" +  " on disk")
            backup_files=input("Do you want to backup? (y/n)\n>> ")
            
            if backup_files=='y':
                sys.stdout.write("\r" + "> Backing up\n")
                for file_info in get_file_list(slack,None,WHOAMI):
                    output_name=file_info['id']+"-"+file_info['name'].replace(':',"_").replace('/',"_")                    
                    sys.stdout.write("\r" + "> Dowloading file: "+output_name)
                    r = session.get(file_info['url_private'])
                    open(output_name, 'wb').write(r.content)
                    sys.stdout.flush()
                    sys.stdout.write("\r" + "> Dowloded file: "+output_name+"\n")
                    #print("Dowloded file: "+output_name)
            
            
            #delete the $h1t out of it
            sys.stdout.write("\r" + "> Deleting files\n")
            delete_files=input(">>>> Are you sure (y/n)\n>> ")
            max_chars=37
            if delete_files != "y":
                    print (">>>> aborted by user")
                    raise
            files_count=0
            for file_info in get_file_list(slack,None,WHOAMI):
                sys.stdout.flush()
                xxx=(file_info['name']).strip().replace("\n","<LN>")[0:max_chars-3]
                xxx+="..."
                if len(xxx)<max_chars:
                    xxx+=" "*(max_chars-len(xxx))
                sys.stdout.write("\r" + xxx)
                if dry_run:
                    time.sleep(0.1)
                files_count+=1
                delete_file(slack,file_info['id']) 
            
            xxx='> Files deleted. Total deleted: '+str(files_count)
            if len(xxx)<max_chars:
                xxx+=" "*(max_chars-len(xxx))
            sys.stdout.write("\r" + xxx+'\n')
        except:
            sys.stdout.flush()
            sys.stdout.write("\r" + "> Files could not be retrived or something happened\n")    
    return 0



def handle_rate_limit(method, *args, **kwargs):
    max_count = 10
    count = max_count
    while count > 0:
        try:
            response = method(*args, **kwargs)
            assert response.successful
            assert response.body['ok']
            return response
        except HTTPError as exception:
            if exception.response.status_code == 429:
                retry_time = int(exception.response.headers['retry-after'])
                retry_time = min(3, retry_time)
                if retry_time > 3:
                    print('Sleeping for {} seconds'.format(retry_time))
                time.sleep(retry_time)
            else:
                raise
        except ReadTimeout:
            sleep_time=(max_count-count+1)*15
            print('Read timeout. Sleeping for '+str(sleep_time)+' seconds')
            time.sleep(sleep_time)
        count -= 1
    raise Exception('Max retries exceeded')

def dont_paginate(method, *args, params=None):
    response = handle_rate_limit(method,*args, params=params)
    assert response.successful
    return response.body

def paginate(method, *args, collection, params=None):
    if params is None:
        params = {'limit': 1000}
    else:
        params.setdefault('limit', 1000)
    while params.get('cursor', True):
        response = handle_rate_limit(method,*args, params=params)
        assert response.successful
        for conversation in response.body[collection]:
            yield conversation
        try:
            if 'response_metadata' in response.body.keys():
                params['cursor'] = response.body['response_metadata']['next_cursor']
            else:
                params['cursor'] = "" 
        except Exception as error:
            print (error)
            print ("poop")
            print (response.body)
            return 0

def get_private_conversations(slack, types):
    paginatezadas = paginate(slack.api.get, 'conversations.list',
            collection='channels', params={'types': types})
    return paginatezadas

def get_private_messages(slack, channel):
    paginatezadas = paginate(slack.api.get, 'conversations.history',
            collection='messages', params={'channel': channel})
    return paginatezadas
    
def get_private_thread_messages(slack, channel,ts):
    paginatezadas = paginate(slack.api.get, 'conversations.replies',
            collection='messages', params={'channel': channel,'ts':ts})
    return paginatezadas

def get_file_info(slack, file):
    paginatezadas = dont_paginate(slack.api.get, 'files.info'
                                  , params={'file': file})['file']
    return paginatezadas

def get_user_me(slack):
    response = handle_rate_limit(slack.api.post, 'auth.test',
                                 data={})
    assert response.successful
    return response.body

def edit_private_message(slack, channel, ts, text):
    if dry_run:
        return {}
    response = handle_rate_limit(slack.api.post, 'chat.update',
                                 data={'channel': channel,"ts" : ts,"text" : text})
    assert response.successful
    return response.body['message']

def delete_private_message(slack, channel, ts):
    if dry_run:
        return {}
    try:
        response = handle_rate_limit(slack.api.post, 'chat.delete',
                                 data={'channel': channel,"ts" : ts})
        assert response.successful
        return response.body
    except slacker.Error as e:
        if str(e) == "message_not_found":
            print ("warning message already deleted")
            return {}
        else:
            raise e
            
def get_remote_files(slack): #no token for this. care cup
    paginatezadas = dont_paginate(slack.api.get, 'files.remote.list',
                                  params={})
    return paginatezadas

def get_file_list(slack, channel,user):
    paginatezadas = paginate(slack.api.get, 'files.list',
            collection='files', params={'channel': channel,'user':user})
    return paginatezadas

def delete_file(slack, file_id):
    if dry_run:
        return {}
    response = handle_rate_limit(slack.api.post, 'files.delete',
                                 data={'file': file_id})
    assert response.successful
    return response.body

def get_reactions_list(slack, user):
    paginatezadas = paginate(slack.api.get, 'reactions.list',
            collection='items', params={'user':user,'limit': 100})
    return paginatezadas

def delete_reaction(slack, name, channel, timestamp):
    if dry_run:
        return {}
    try:
        response = handle_rate_limit(slack.api.post, 'reactions.remove',
                                 data={'name':name,'channel' : channel, 'timestamp' : timestamp})
        assert response.successful
        return response.body
    except Exception as e:
        if str(e) == "no_reaction":
            print ("warning reaction already deleted. its a bug. ignore")
            return {}
        else:
            raise e
        



def get_private_IM_channel(slack, users):
    dicionariozadas={}
    for conversation in get_private_conversations(slack, 'im'):
        if message_count(slack, conversation['id']) <= 0:
            continue
        userzadas=users[conversation['user']]
        dicionariozadas[userzadas]=conversation['id']
    return dicionariozadas

def get_private_IM_messages_from_channel(slack, users):
    dicionariozadas={}
    for message in get_private_messages(slack, users):
        #print (message)
        #if its a thread then check inside it. else regular message parsing
        if 'thread_ts' in message.keys():
            for thread_message in get_private_thread_messages(slack, users,message['thread_ts']):
                dicionariozadas[thread_message['ts']]=thread_message
        dicionariozadas[message['ts']]=message
    return dicionariozadas


def message_count(slack, channel):
    response = handle_rate_limit(slack.api.post, 'search.messages',
                                 data={'query': 'in:<#{}>'.format(channel)})
    assert response.successful
    return response.body['messages']['total']

def users(slack):
    by_id = {}
    for user in paginate(slack.api.get, 'users.list', collection='members'):
        by_id[user['id'] ] = user['name']
    return by_id


if __name__ == '__main__':
    sys.exit(main())
