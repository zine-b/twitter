import argparse
import socket
import time
import traceback
from datetime import date
from datetime import timedelta
from utils import read_one_block_of_yaml_data
import requests

properties = {}

def create_url(keyword, end_date, next_token=None, max_results=10):
    #search_url = "https://api.twitter.com/2/tweets/search/recent"
    search_url = properties['twitter']['api-url'] + "/2/tweets/search/recent"

    query_params = {'query': keyword,
                    'end_time': end_date,
                    'max_results': max_results,
                    'tweet.fields': 'id,text,author_id,geo,conversation_id,created_at,lang,entities',
                    'next_token': next_token
                    }
    return (search_url, query_params)


def get_response(url, headers, params):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def get_tweet_data(next_token=None, query='corona', max_results=20):
    bearer_token = properties['twitter']['token']
    headers = {"Authorization": f"Bearer {bearer_token}"}
    keyword = f"{query} lang:en has:hashtags"

    end_date = str(date.today() - timedelta(days=6))
    end_time = f"{end_date}T00:00:00.000Z"

    url: tuple = create_url(keyword, end_time, next_token=next_token, max_results=20)
    json_response = get_response(url=url[0], headers=headers, params=url[1])

    import json
    with open(properties['spark']['file-path'], 'w+') as teeee:
        json.dump(json_response, teeee, indent=2)

    return json_response


def get_hashtag(tag_info: dict):
    tag = str(tag_info['tag']).strip()
    hashtag = str('#' + tag + '\n')
    print(f"Hashtag: {hashtag.strip()}")
    return hashtag


def send_tweets_to_spark(http_resp, tcp_connection):
    data: list = http_resp["data"]
    for tweet in data:
        try:
            hashtag_list = tweet['entities']['hashtags']
            for tag_info in hashtag_list:
                hashtag = get_hashtag(tag_info)
                tcp_connection.send(hashtag.encode("utf-8"))
        except KeyError:
            print("No hashtag found in current tweet, moving on...")
            continue
        except BrokenPipeError:
            exit("Pipe Broken, Exiting...")
        except KeyboardInterrupt:
            exit("Keyboard Interrupt, Exiting...")
        except Exception as e:
            traceback.print_exc()


def input_term():
    parser = argparse.ArgumentParser(description='Spark Tweet analyzer')
    parser.add_argument('-p', '--pages', type=int, help="No of pages to query", required=True)
    parser.add_argument('-k', '--keywords', type=str, help="List of keywords to query", required=True)
    parser.add_argument('-m', '--max_results', type=int, help="max results", required=False)
    parser.add_argument('-s', '--sleep_timer', type=float, help="sleep timer", required=False)

    args = parser.parse_args()

    return args.pages, args.keywords, args.max_results, args.sleep_timer


if __name__ == '__main__':
    properties = read_one_block_of_yaml_data('local-properties.yml')
    # queries = ['corona', 'bitcoin', 'gaming', 'Android']
    no_of_pages, queries, max_results, sleep_timer = input_term()
    if max_results is None:
        max_results = 20
    if sleep_timer is None:
        sleep_timer = 5

    queries = str(queries).split(" ")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((properties['spark']['host'], properties['spark']['port']))
    s.listen(1)
    print("Waiting for the TCP connection...")

    conn, addr = s.accept()
    print("Connected successfully... Starting getting tweets.")

    next_token = None
    for query in queries:
        for _ in range(no_of_pages):
            try:
                print(f"\n\n\t\tProcessing Page {_} for keyword {query}\n\n")
                resp = get_tweet_data(next_token=next_token, query=query, max_results=max_results)
                next_token = resp['meta']['next_token']
                send_tweets_to_spark(http_resp=resp, tcp_connection=conn)
                time.sleep(sleep_timer)
            except KeyboardInterrupt:
                exit("Keyboard Interrupt, Exiting..")
